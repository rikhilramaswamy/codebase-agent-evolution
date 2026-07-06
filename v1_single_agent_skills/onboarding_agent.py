"""
Orchestrates the codebase onboarding agent using a supervisor-worker pattern.

This module provides the main entry point for the V1 agent runner, which delegates
semantic search and graph inspection tasks to isolated skill scripts executed
as subprocesses.
"""
import os
import sys
import subprocess
import json

# Ensure shared utilities are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import LlmAgent
from google.adk.planners import PlanReActPlanner
from google.adk.runners import InMemoryRunner

# Paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Helper to run skills
def _run_skill_script(script_path: str, **kwargs) -> str:
    """
    Executes an external skill script as a subprocess and captures its output.

    Args:
        script_path: The filesystem path to the Python skill script.
        **kwargs: Command-line arguments to pass to the script.

    Returns:
        The standard output of the subprocess as a string, or an error message.
    """
    # Construct command: python /path/to/script.py --arg1 val1 --arg2 val2 ...
    command = [sys.executable, script_path]
    for key, value in kwargs.items():
        if value is not None:
            command.extend([f"--{key}", str(value)])

    # Prepare environment for the subprocess
    env = os.environ.copy()
    env["CHROMA_DB_PATH"] = os.path.join(DATA_DIR, "chroma_db")
    env["CODE_GRAPH_PATH"] = os.path.join(DATA_DIR, "codebase.graphml")
    # Explicitly pass the API key if it exists in the parent env
    if "GOOGLE_API_KEY" in os.environ:
        env["GOOGLE_API_KEY"] = os.environ["GOOGLE_API_KEY"]
    try:
        # Subprocess inherits updated environment
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=BASE_DIR,
            env=env
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error executing skill: {e.stderr}"

# --- Explicit Tool Definitions ---

def code_semantic_search(query: str, n_results: int = 3) -> str:
    """
    Executes the semantic search skill to find relevant code snippets.

    Args:
        query: Natural language query about codebase contents.
        n_results: Number of snippets to return.
    """
    script_path = os.path.join(SKILLS_DIR, "code_semantic_search", "search_chroma.py")
    return _run_skill_script(script_path, query=query, n_results=n_results)

def code_graph_inspection(action: str, function_name: str) -> str:
    """
    Executes the graph inspection skill to analyze codebase structural relationships.

    Args:
        action: Type of inspection ("find_callers" or "find_callees").
        function_name: The name of the function to inspect.
    """
    script_path = os.path.join(SKILLS_DIR, "code_graph_inspection", "inspect_networkx.py")
    return _run_skill_script(script_path, action=action, function_name=function_name)

# --- Runner Setup ---

def main(adk_model):
    """
    Initializes and returns the agent configured with semantic and structural tools.
    """
    # Register explicit tools
    tools = [code_semantic_search, code_graph_inspection]

    # Initialize Agent with Planner
    planner = PlanReActPlanner()
    agent = LlmAgent(
        name="OnboardingAgent",
        model=adk_model,
        planner=planner,
        tools=tools,
        instruction="You are an expert software engineering assistant. Use the provided skills to answer questions about the codebase."
    )

    print(f"Agent runner ready and initialized with {len(tools)} skills.")
    return agent

async def start_interactive_chat(agent):
    """Starts an interactive command-line chat session with the agent using InMemoryRunner."""
    runner = InMemoryRunner(agent=agent)

    print("\n--- Codebase Q&A Agent is Ready ---")
    print("Enter your questions below. Type 'exit' to quit.")

    while True:
        try:
            question = input("\n> ")
            if question.lower() == 'exit':
                print("Exiting...")
                break

            # Using run_debug as established in buffer/driver.py
            await runner.run_debug(question)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    pass