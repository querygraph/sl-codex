from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(relative_path: str) -> str:
    return subprocess.check_output(
        [sys.executable, str(ROOT / relative_path)],
        cwd=ROOT,
        text=True,
    )


class ExampleTests(unittest.TestCase):
    def test_querygraph_bundle_contains_osi_model(self) -> None:
        output = run_script("examples/querygraph/build_ai_navigator_bundle.py")
        bundle = json.loads(output)

        self.assertEqual(
            bundle["querygraph:semanticModel"]["format"],
            "open-semantic-interchange",
        )
        self.assertIn("identity", bundle)
        self.assertIn("odrl", bundle["layers"])

    def test_polaris_registration_payload_links_bundle_and_lineage(self) -> None:
        output = run_script("examples/polaris/register_semantic_model.py")
        _, raw_json = output.split("\n", 1)
        payload = json.loads(raw_json)

        self.assertEqual(payload["resourceType"], "SemanticModel")
        self.assertEqual(payload["target"]["identifier"], "lakehouse.analytics.orders")
        self.assertEqual(
            payload["semanticModel"]["semantic_models"][0]["metrics"][0]["name"],
            "total_revenue",
        )
        self.assertEqual(
            payload["lineage"]["registrationEvent"]["job"]["namespace"],
            "apache-polaris",
        )

    def test_openlineage_event_has_semantic_facet(self) -> None:
        output = run_script("examples/openlineage/semantic_model_event.py")
        event = json.loads(output)
        facet = event["job"]["facets"]["querygraph_semantic_model"]

        self.assertEqual(event["eventType"], "COMPLETE")
        self.assertEqual(facet["semanticModel"], "revenue_semantics")
        self.assertEqual(facet["format"], "open-semantic-interchange")
        self.assertTrue(facet["querygraphBundleHash"].startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
