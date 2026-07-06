---
name: code_semantic_search
description: "Use this skill to find relevant code snippets based on a natural language query about the codebase contents."
parameters:
  type: object
  properties:
    query:
      type: string
      description: "The natural language query describing the code you are looking for."
    n_results:
      type: integer
      description: "Number of code snippets to return (default: 3)."
  required:
    - query
---