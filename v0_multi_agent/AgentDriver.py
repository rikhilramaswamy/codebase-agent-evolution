"""
Defines the interactive chat loop for the Codebase Onboarding Agent.

This script provides the `start_chat` function, which creates an `InMemoryRunner` 
for the main `QueryManagerAgent` and enters a loop to accept user input. 
It is the primary entry point for interacting with the agent in a live session.
"""
import asyncio
import os
import sys

# Ensure shared utilities and the v0_multi_agent folder are importable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from google.adk.runners import InMemoryRunner
from shared.config_setup import setup_environment_and_models
from QueryManagerAgent import build_query_manager_agent

# --- Interactive Q&A Loop ---
async def start_chat(agent):
    """Starts an interactive command-line chat session with the QueryManagerAgent."""
    # Ensure the agent was imported/defined correctly
    if not hasattr(agent, 'name'):
        print("QueryManagerAgent is not defined correctly. Cannot start chat.")
        return

    runner = InMemoryRunner(agent=agent)

    print("\n--- Codebase Q&A is Ready ---")
    print("Enter your questions below. Type 'exit' to quit.")

    while True:
        try:
            question = input("\n> ")
            if question.lower() == 'exit':
                print("Exiting...")
                break
            
            # Use await and run_debug
            await runner.run_debug(question)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

async def run():
    adk_model, chroma_client, embedding_model, code_graph = setup_environment_and_models()
    if adk_model and chroma_client and embedding_model and code_graph:
        agent = build_query_manager_agent(adk_model, chroma_client, embedding_model, code_graph)
        await start_chat(agent)
    else:
        print("Failed to initialize agent dependencies.")

if __name__ == "__main__":
    asyncio.run(run())


