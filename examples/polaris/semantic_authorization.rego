package polaris.semantic

default allow := false

semantic_actions := {
  "SEMANTIC_MODEL_CREATE",
  "SEMANTIC_MODEL_READ",
  "SEMANTIC_MODEL_ALTER",
  "SEMANTIC_MODEL_DROP",
  "SEMANTIC_MODEL_VALIDATE",
  "SEMANTIC_MODEL_USE",
}

allow if {
  input.action in semantic_actions
  input.principal.role == "admin"
}

allow if {
  input.action == "SEMANTIC_MODEL_READ"
  input.principal.role == "analyst"
  input.resource.catalog == "lakehouse"
}

allow if {
  input.action == "SEMANTIC_MODEL_USE"
  input.principal.role == "agent"
  input.resource.catalog == "lakehouse"
  not odrl_prohibits_ai_use
}

odrl_prohibits_ai_use if {
  some prohibition in input.resource.querygraphBundle.inline.layers.odrl["odrl:prohibition"]
  prohibition["odrl:action"] == "odrl:use"
  prohibition["odrl:assignee"] == input.principal.did
}
