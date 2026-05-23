"""Mappings between OSI, QueryGraph, Polaris, and OpenLineage examples."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .model import OsiSemanticModel


PRODUCER = "https://querygraph.ai/polaris-ai-navigator"
SEMANTIC_FACET_SCHEMA = (
    "https://querygraph.ai/schemas/openlineage/semantic-model-facet.json"
)


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def stable_sha256(data: Any) -> str:
    return "sha256:" + hashlib.sha256(_stable_json(data).encode("utf-8")).hexdigest()


def _repo_root() -> Path:
    # mapping.py is semantic/codex/src/qg_polaris_semantic/mapping.py.
    return Path(__file__).resolve().parents[4]


def _load_querygraph_reference() -> tuple[type[Any], type[Any]]:
    qg_python = _repo_root() / "qg-python"
    if qg_python.exists():
        sys.path.insert(0, str(qg_python))

    try:
        from querygraph import AiNavigator, NavigatorInput
    except ImportError as exc:  # pragma: no cover - exercised only off-repo.
        raise RuntimeError(
            "The QueryGraph Python reference implementation was not found. "
            f"Expected it at {qg_python}."
        ) from exc

    return AiNavigator, NavigatorInput


def build_querygraph_bundle(model: OsiSemanticModel) -> dict[str, Any]:
    """Build a QueryGraph AI Navigator JSON-LD bundle for an OSI model."""

    AiNavigator, NavigatorInput = _load_querygraph_reference()
    navigator_input = NavigatorInput(
        dataset_name=model.name,
        description=model.description,
        landing_page=model.landing_page,
        data_url=model.data_url,
        creator=model.owner,
        agent_name="QueryGraph AI Navigator for Apache Polaris",
    )

    bundle = AiNavigator().build(navigator_input).bundle
    bundle["querygraph:semanticModel"] = {
        "format": "open-semantic-interchange",
        "formatVersion": "0.1",
        "target": {
            "type": "iceberg-table",
            "identifier": model.iceberg_identifier,
        },
        "definition": model.to_osi_dict(),
    }
    bundle["querygraph:semanticModelHash"] = stable_sha256(model.to_osi_dict())
    return bundle


def openlineage_event(model: OsiSemanticModel, bundle: dict[str, Any]) -> dict[str, Any]:
    """Return an OpenLineage event with a QueryGraph semantic model facet."""

    bundle_hash = stable_sha256(bundle)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    semantic_facet = {
        "_producer": PRODUCER,
        "_schemaURL": SEMANTIC_FACET_SCHEMA,
        "semanticModel": model.name,
        "format": "open-semantic-interchange",
        "target": model.iceberg_identifier,
        "querygraphBundleHash": bundle_hash,
        "didIssuer": bundle.get("identity", {}).get("id"),
        "odrlPolicy": bundle.get("layers", {}).get("odrl", {}).get("@id"),
    }

    return {
        "eventTime": now,
        "eventType": "COMPLETE",
        "producer": PRODUCER,
        "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json",
        "job": {
            "namespace": "apache-polaris",
            "name": f"semantic-model/register/{model.name}",
            "facets": {
                "querygraph_semantic_model": semantic_facet,
            },
        },
        "run": {
            "runId": hashlib.sha256(f"{model.name}:{bundle_hash}".encode()).hexdigest(),
            "facets": {},
        },
        "inputs": [
            {
                "namespace": f"iceberg://{model.catalog}",
                "name": f"{model.namespace}.{model.table}",
                "facets": {
                    "querygraph_semantic_model": semantic_facet,
                },
            }
        ],
        "outputs": [
            {
                "namespace": "polaris://lakehouse",
                "name": f"{model.namespace}.semantic_models.{model.name}",
                "facets": {
                    "querygraph_semantic_model": semantic_facet,
                },
            }
        ],
    }


def polaris_registration_payload(
    model: OsiSemanticModel,
    bundle: dict[str, Any],
) -> dict[str, Any]:
    """Return a proposed Polaris semantic model registration payload."""

    event = openlineage_event(model, bundle)
    bundle_hash = stable_sha256(bundle)

    return {
        "catalog": model.catalog,
        "namespace": [model.namespace],
        "name": model.name,
        "resourceType": "SemanticModel",
        "format": "open-semantic-interchange",
        "formatVersion": "0.1",
        "target": {
            "type": "iceberg-table",
            "identifier": model.iceberg_identifier,
        },
        "semanticModel": model.to_osi_dict(),
        "querygraphBundle": {
            "format": "querygraph-ai-navigator-jsonld",
            "inline": bundle,
            "hash": bundle_hash,
        },
        "lineage": {
            "openLineageProducer": PRODUCER,
            "registrationEvent": event,
        },
        "policyHints": {
            "odrlPolicy": bundle.get("layers", {}).get("odrl", {}),
            "recommendedPrivilege": "SEMANTIC_MODEL_USE",
        },
    }
