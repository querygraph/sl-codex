#!/usr/bin/env python3
"""Emit an OpenLineage event for semantic model registration."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qg_polaris_semantic import (
    build_querygraph_bundle,
    example_revenue_model,
    openlineage_event,
)


def main() -> None:
    model = example_revenue_model()
    bundle = build_querygraph_bundle(model)
    event = openlineage_event(model, bundle)
    print(json.dumps(event, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

