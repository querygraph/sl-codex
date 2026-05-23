# QueryGraph AI Navigator for Apache Polaris Semantics

This repository is a companion artifact for the semantic layer review in
`REPORT.md`. It shows how an Open Semantic Interchange style semantic model can
be wrapped with QueryGraph AI Navigator metadata and registered with a proposed
Apache Polaris semantic model API.

The examples are intentionally small and dependency-free. They use the local
`qg-python` reference implementation when it is available at
`/Users/alexy/src/querygraph/qg-python`.

## Layout

- `REPORT.md` - comprehensive review and integration proposal.
- `src/qg_polaris_semantic/` - small Python model and mapping helpers.
- `examples/osi/` - an OSI-style YAML semantic model.
- `examples/querygraph/` - builds a QueryGraph AI Navigator JSON-LD bundle.
- `examples/polaris/` - proposed Polaris registration payload, OpenAPI sketch,
  and OPA policy sketch.
- `examples/openlineage/` - emits an OpenLineage event with a semantic facet.
- `tests/` - verifies the examples produce coherent, compatible JSON.

## Run

```bash
python3 examples/querygraph/build_ai_navigator_bundle.py
python3 examples/polaris/register_semantic_model.py
python3 examples/openlineage/semantic_model_event.py
python3 -m unittest discover -s tests
```

## Core Idea

Polaris should treat semantics as governed catalog metadata:

1. Store OSI semantic models as first-class catalog resources attached to
   Iceberg tables, views, namespaces, or catalogs.
2. Allow QueryGraph AI Navigator bundles to enrich those resources with
   Croissant, CDIF, DID, and ODRL metadata for AI agents and open data spaces.
3. Emit OpenLineage facets whenever semantic models are registered, compiled,
   or used in query planning.
4. Enforce access through Polaris privileges and external PDP/OPA integration,
   while using ODRL as portable rights metadata rather than as the only
   enforcement mechanism.

