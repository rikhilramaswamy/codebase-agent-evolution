"""
Agent Driver for the Codebase Onboarding Agent (V1).

This module serves as the primary entry point for executing the V1 agent runner, 
which uses modular skills executed as subprocesses. It initializes the 
environment and launches the interactive chat loop.
"""

import asyncio
import os
import sys

# Ensure shared utilities are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from onboarding_agent import main, start_interactive_chat
from shared.config_setup import setup_environment_and_models

async def run():
    adk_model, _, _, _ = setup_environment_and_models()
    agent = main(adk_model)
    await start_interactive_chat(agent)

if __name__ == "__main__":
    asyncio.run(run())