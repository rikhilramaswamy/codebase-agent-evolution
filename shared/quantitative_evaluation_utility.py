"""
Quantitative Evaluation Utility

This script provides a utility function to run a quantitative benchmark on the 
agent system. It is designed to be imported and used within the main Kaggle 
notebook after the agent has been initialized.

The `run_quantitative_benchmark` function takes a list of questions, executes 
them against the agent, and measures key performance indicators:
- Latency (in seconds)
- Total Token Consumption
"""

import asyncio
import time
import pandas as pd
import warnings
from google.adk.runners import InMemoryRunner

# Suppress warnings
try:
    from suppress_warnings import _warning_filter
except ImportError:
    import logging
    logging.getLogger('google_genai.types').setLevel(logging.ERROR)
    warnings.filterwarnings('ignore', message='.*non-text parts in the response.*')
    warnings.filterwarnings('ignore', category=UserWarning, module='google_genai')

async def run_quantitative_benchmark(questions: list, agent):
    """
    Runs a list of questions against the agent, measures performance, 
    and prints a summary table. 

    Args:
        questions: A list of strings, where each string is a question for the agent.
        agent: The fully initialized agent object to be benchmarked.
    """
    if not hasattr(agent, 'name'):
        print("❌ ERROR: Agent is not defined correctly. Cannot run benchmark.")
        return

    runner = InMemoryRunner(agent=agent)
    results = []

    print("🚀 Starting Quantitative Benchmark...")

    for i, question in enumerate(questions):
        print(f"--- Running Question {i+1}/{len(questions)} ---")
        print(f"> {question}")

        start_time = time.time()

        # The response is a list of steps the agent took
        response_steps = await runner.run_debug(question)

        end_time = time.time()
        latency = end_time - start_time

        total_tokens = 0
        # Sum up tokens from all steps in the agent's reasoning process
        if isinstance(response_steps, list):
            for step in response_steps:
                # The response structure might vary slightly; check for usage_metadata
                if hasattr(step, 'usage_metadata') and step.usage_metadata:
                    total_tokens += step.usage_metadata.total_token_count
                elif hasattr(step, 'response') and hasattr(step.response, 'usage_metadata'):
                    # Sometimes tokens are nested under a response object
                    total_tokens += step.response.usage_metadata.total_token_count

        results.append({
            "Question": f"'{question[:50]}...'",
            "Latency (s)": f"{latency:.2f}",
            "Total Tokens": total_tokens
        })

    print("\n--- Benchmark Complete ---")

    # --- Display Results in a Markdown Table ---
    df = pd.DataFrame(results)
    print("\n### Performance Benchmark\n")
    print(df.to_markdown(index=False))

if __name__ == '__main__':
    # --- Example Usage in a Kaggle Notebook ---
    #
    # 1. Define the benchmark questions:
    benchmark_questions = [
            "Explain the entire document processing pipeline. Start by finding the main function for creating the RAG chain,then trace its data flow to see how documents are retrieved and vectorized.",
            "Show me the code for the vector_retriever function, and then find all the functions that it calls",
            "Find out what function calls get_urls and then show me the source code of that calling function"
    ]
    #
    # 2. Call the benchmark function with the questions and the main agent:
    # Initialize the agent (it automatically loads skills from./skills/)
    agent = main(adk_model)
    await run_quantitative_benchmark(benchmark_questions, agent)
    print("✅ Quantitative evaluation module is defined and ready to be used.")