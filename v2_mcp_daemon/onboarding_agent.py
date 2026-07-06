"""
Onboarding agent orchestrator using MCP toolsets.

This module sets up an LLM agent configured with MCP tools, enabling
semantic search and codebase graph inspection through an MCP server interface.
"""

import os
import sys

# Ensure shared utilities are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import LlmAgent
from google.adk.planners import PlanReActPlanner
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp.client.stdio import StdioServerParameters

# ADK default MCP stdio timeout is 5s — server imports need longer on cold start.
MCP_SESSION_TIMEOUT_SECONDS = 120.0

# Paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MCP_SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
DATA_DIR = os.path.join(BASE_DIR, "data")


def _build_mcp_env():
    """
    Constructs the environment variables required for the MCP server process.
    """
    env = os.environ.copy()

    env["CHROMA_DB_PATH"] = os.path.join(DATA_DIR, "chroma_db")
    env["CODE_GRAPH_PATH"] = os.path.join(DATA_DIR, "codebase.graphml")
    env["PYTHONPATH"] = BASE_DIR
    env["PYTHONUNBUFFERED"] = "1"
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if gemini_key:
        env["GEMINI_API_KEY"] = gemini_key
    return env


def build_mcp_toolset():
    """
    Creates an McpToolset configured with StdioConnectionParams.

    Returns:
        An instance of McpToolset configured with the MCP server command,
        arguments, environment, and timeout.
    """
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[MCP_SERVER_PATH],
                env=_build_mcp_env(),
            ),
            timeout=MCP_SESSION_TIMEOUT_SECONDS,
        )
    )


def main(adk_model):
    """
    Initializes and returns an LlmAgent configured with the MCP Toolset.

    Args:
        adk_model: The LLM model instance to use for the agent.

    Returns:
        An configured instance of LlmAgent.
    """
    codebase_toolset = build_mcp_toolset()

    planner = PlanReActPlanner()
    agent = LlmAgent(
        name="OnboardingAgent",
        model=adk_model,
        planner=planner,
        tools=[codebase_toolset],
        instruction=(
            "You are an expert software engineering assistant. Use the connected "
            "codebase data port tool to answer questions about the codebase."
        ),
    )

    print("Agent runner initialized with MCP Toolset.")
    print(f"  MCP server: {MCP_SERVER_PATH}")
    print(f"  MCP timeout: {MCP_SESSION_TIMEOUT_SECONDS}s")
    return agent


async def start_interactive_chat(agent):
    """
    Starts an interactive command-line chat session with the agent using InMemoryRunner.

    Args:
        agent: The LlmAgent instance to interact with.
    """
    runner = InMemoryRunner(agent=agent)

    print("\n--- Codebase Q&A Agent is Ready (MCP Mode) ---")
    print("Enter your questions below. Type 'exit' to quit.")

    while True:
        try:
            question = input("\n> ")
            if question.lower() == "exit":
                print("Exiting...")
                break

            await runner.run_debug(question)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")