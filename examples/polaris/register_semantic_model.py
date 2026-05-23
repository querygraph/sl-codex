#!/usr/bin/env python3
"""Print a proposed Polaris semantic model registration request."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qg_polaris_semantic import (
    build_querygraph_bundle,
    example_revenue_model,
    polaris_registration_payload,
)


def main() -> None:
    model = example_revenue_model()
    bundle = build_querygraph_bundle(model)
    payload = polaris_registration_payload(model, bundle)
    endpoint = (
        f"/api/catalogs/{model.catalog}/namespaces/{model.namespace}"
        "/semantic-models"
    )
    print(f"POST {endpoint}")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

