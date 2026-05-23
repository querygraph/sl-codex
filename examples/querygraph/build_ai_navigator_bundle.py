#!/usr/bin/env python3
"""Build a QueryGraph AI Navigator bundle for the OSI example."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from qg_polaris_semantic import build_querygraph_bundle, example_revenue_model


def main() -> None:
    model = example_revenue_model()
    bundle = build_querygraph_bundle(model)
    print(json.dumps(bundle, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

