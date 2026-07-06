"""
Defines the main QueryManagerAgent, the "Supervisor" of the multi-agent system.

This agent is responsible for understanding a user's query, creating a 
step-by-step plan using the PlanReActPlanner, and delegating tasks to the
specialist worker agents (SemanticSearchAgent and GraphInspectorAgent).
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.planners import PlanReActPlanner

import SemanticSearchAgent
import GraphInspectorAgent

def build_query_manager_agent(adk_model, chroma_client, embedding_model, code_graph):
    """
    Builds and returns the QueryManagerAgent, configured with its worker agents.
    """
    # 1. Initialize workers
    semantic_search_worker = SemanticSearchAgent.build_semantic_search_agent(adk_model)
    SemanticSearchAgent.set_dependencies(chroma_client, embedding_model)

    graph_inspector_worker = GraphInspectorAgent.build_graph_inspector_agent(adk_model)
    GraphInspectorAgent.set_dependencies(code_graph)

    # 2. Instantiate the planner
    planner = PlanReActPlanner()

    # 3. Define the Supervisor Agent and attach the planner
    QueryManagerAgent = LlmAgent(
        name="QueryManagerAgent",
        model=adk_model,
        planner=planner,
        instruction=(
            "You are a master software engineering assistant. Your goal is to answer "
            "complex questions about a codebase by creating a plan and then delegating "
            "tasks to your specialist assistants.\n\n"
            "You have access to the following assistants as tools:\n"
            "- **SemanticSearchAgent**: Use this assistant to answer 'what is' or 'where is' questions. "
            "It is an expert at finding relevant code snippets based on natural language descriptions.\n"
            "- **GraphInspectorAgent**: Use this assistant to answer questions about code structure and "
            "relationships, like 'who calls function X' or 'what does function Y call'. "
            "It requires an exact function name as input.\n\n"
            "For any user query, you must first create a step-by-step plan. Then, execute the plan."
        ),
        tools=[
            AgentTool(agent=semantic_search_worker),
            AgentTool(agent=graph_inspector_worker)
        ]
    )
    return QueryManagerAgent