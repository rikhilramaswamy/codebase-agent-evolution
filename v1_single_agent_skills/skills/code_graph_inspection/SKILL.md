---
name: code_graph_inspection
description: "Use this tool to analyze relationships in the codebase, specifically for finding function callers and callees."
parameters:
  type: object
  properties:
    action:
      type: string
      enum: ["find_callers", "find_callees"]
      description: "The type of relationship to inspect."
    function_name:
      type: string
      description: "The exact name of the function to inspect."
  required:
    - action
    - function_name
---