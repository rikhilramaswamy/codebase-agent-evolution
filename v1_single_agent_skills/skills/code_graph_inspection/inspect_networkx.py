"""
Performs structural analysis on a codebase using a NetworkX call graph.

This script acts as a standalone skill for the agent, allowing it to inspect
function relationships (callers and callees) within the codebase. It expects
the path to the GraphML file to be provided via environment variables.
"""
import argparse
import json
import os
import networkx as nx

def main():
    """
    Parses command-line arguments, loads the codebase graph, and performs
    structural inspection (finding callers or callees) for a given function.
    """
    parser = argparse.ArgumentParser(description="Code graph inspection skill.")
    parser.add_argument("--action", type=str, required=True, choices=["find_callers", "find_callees"], help="Relationship to inspect.")
    parser.add_argument("--function_name", type=str, required=True, help="Function to inspect.")
    args = parser.parse_args()

    # Access persisted graph
    graph_path = os.environ.get("CODE_GRAPH_PATH", "./codebase.graphml")
    if not os.path.exists(graph_path):
        print(json.dumps({"error": f"Graph file not found at {graph_path}"}))
        return

    # Load graph
    G = nx.read_graphml(graph_path)

    # Try exact match
    target_node = None
    if args.function_name in G:
        target_node = args.function_name
    else:
        # Try finding a node that ends with the target name (e.g. module.func)
        for node in G.nodes():
            if node.endswith(f".{args.function_name}"):
                target_node = node
                break

    if target_node is None:
        # Return a list of potential matches
        potential_matches = [node for node in G.nodes() if args.function_name.lower() in node.lower()]
        print(json.dumps({"error": f"Function {args.function_name} not found.", "suggestions": potential_matches[:10]}))
        return

    results = []
    if args.action == "find_callers":
        results = list(G.predecessors(target_node))
    elif args.action == "find_callees":
        results = list(G.successors(target_node))

    print(json.dumps({"results": results, "resolved_function_name": target_node}))

if __name__ == "__main__":
    main()