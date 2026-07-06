"""
Defines the GraphInspectorAgent and its associated tools.

This agent acts as the "structural expert" in the multi-agent system. It is 
responsible for traversing the NetworkX code graph to find function callers
and callees. 
"""

from google.adk.agents import LlmAgent

# Global state for dependency
_code_graph = None

def set_dependencies(code_graph):
    """Sets the dependencies required for graph inspection."""
    global _code_graph
    _code_graph = code_graph

# --- Custom Tool Definitions (Simple Functions) ---
def find_callers(function_name: str) -> str:
    """
    Finds all functions that directly call a given function.

    Args:
        function_name: The exact name of the function to find callers for.

    Returns:
        A formatted string listing all functions that call the given function.
    """
    if _code_graph is None: 
        return "Graph data is not loaded. Cannot perform search."

    # Clean the input from the LLM (removes leading/trailing spaces)
    cleaned_name = function_name.strip()

    # Find the full node name in the graph by checking for an exact match or a matching suffix.
    target_node = None
    for node in _code_graph.nodes:
        if node.endswith(f'.{cleaned_name}') or node == cleaned_name:
            target_node = node
            break

    if target_node:
        callers = list(_code_graph.predecessors(target_node))
        if not callers:
            return f"The function '{target_node}' exists but has no direct callers."
        return f"The following functions call '{target_node}':\n- " + "\n- ".join(callers)
    else:
        return f"No function matching '{cleaned_name}' was found in the code graph."

def find_callees(function_name: str) -> str:
    """
    Finds all functions that are directly called by a given function.

    Args:
        function_name: The exact name of the function to find callees for.

    Returns:
        A formatted string listing all functions called by the given function.
    """
    if _code_graph is None: 
        return "Graph data is not loaded. Cannot perform search."

    cleaned_name = function_name.strip()

    # Find the full node name in the graph by checking for an exact match or a matching suffix.
    target_node = None
    for node in _code_graph.nodes:
        if node.endswith(f'.{cleaned_name}') or node == cleaned_name:
            target_node = node
            break

    if target_node:
        callees = list(_code_graph.successors(target_node))
        if not callees:
            return f"The function '{target_node}' exists but does not call any other functions."
        return f"The function '{target_node}' calls the following functions:\n- " + "\n- ".join(callees)
    else:
        return f"No function matching '{cleaned_name}' was found in the code graph."

# --- Graph Inspector Agent Definition ---
def build_graph_inspector_agent(adk_model):
    return LlmAgent(
        name="GraphInspectorAgent",
        model=adk_model,
        instruction=(
            "You are an expert code graph analyst. Your job is to use the "
            "`find_callers` and `find_callees` tools to answer questions about "
            "the relationships between functions in a codebase. Only use the provided tools."
        ),
        tools=[find_callers, find_callees]
    )