
"""
MCP server for codebase onboarding using FastMCP.

This module provides an MCP server interface that facilitates semantic search and
graph-based structural analysis of the codebase, employing lazy loading of resources
to ensure efficient startup before the MCP handshake.
"""

import os
import sys

# Earliest possible telemetry — survives import failures and unbuffered in Kaggle.
def _bootstrap_log(message: str) -> None:
    """
    Logs bootstrap messages to stderr and a log file for early debugging.

    Args:
        message: The message string to log.
    """
    line = f"[mcp_server] {message}\n"
    sys.stderr.write(line)
    sys.stderr.flush()
    for path in ("/tmp/mcp_server.log", os.path.join(os.path.dirname(os.path.abspath(__file__)), "server_init.log")):
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(line)
        except OSError:
            pass

_bootstrap_log("process starting")

import logging
import traceback
import asyncio
import threading

try:
    import chromadb
    import networkx as nx
    from mcp.server.fastmcp import FastMCP
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from chromadb import EmbeddingFunction, Documents, Embeddings
    _bootstrap_log("imports OK")
except Exception:
    _bootstrap_log("IMPORT FAILURE:\n" + traceback.format_exc())
    raise

# Define base directory for locating resource files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Data storage relative to BASE_DIR (one level up)
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

# Setup logging handlers
log_handlers = [logging.StreamHandler(sys.stderr)]
for log_file in (os.path.join(BASE_DIR, "mcp_server.log"), os.path.join(BASE_DIR, "server_init.log")):
    try:
        log_handlers.append(logging.FileHandler(log_file))
    except OSError as e:
        _bootstrap_log(f"FileHandler unavailable for {log_file}: {e}")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=log_handlers,
    force=True,
)
logger = logging.getLogger("mcp_server")

# Initialize MCP server
mcp = FastMCP("Codebase Onboarding MCP Server")

# Global variables for lazy initialization
VECTOR_COLLECTION = None
CODE_GRAPH = None
_init_lock = threading.Lock()
_initialized = False
_init_error = None


def _get_embedding_function():
    """
    Creates and returns a LangChain embedding function for ChromaDB.

    Returns:
        An instance of EmbeddingFunction configured with Gemini.

    Raises:
        ValueError: If (GOOGLE_API_KEY) is not set.
    """
    api_key =  os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("(GOOGLE_API_KEY) is not set!")

    embedding_model = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=api_key,
    )

    class LangchainEmbeddingFunction(EmbeddingFunction):
        def __init__(self):
            pass

        def __call__(self, input: Documents) -> Embeddings:
            return embedding_model.embed_documents(input)

    return LangchainEmbeddingFunction()


def _ensure_initialized():
    """
    Lazy loads ChromaDB and the Code Graph on the first tool call.

    This ensures that heavy resource loading does not delay the initial
    MCP server handshake.

    Raises:
        Exception: If initialization fails.
    """
    global VECTOR_COLLECTION, CODE_GRAPH, _initialized, _init_error

    if _initialized:
        return
    if _init_error is not None:
        raise _init_error

    with _init_lock:
        if _initialized:
            return
        if _init_error is not None:
            raise _init_error

        try:
            # Determine resource paths relative to BASE_DIR/data
            chroma_path = os.environ.get(
                "CHROMA_DB_PATH", os.path.join(DATA_DIR, "chroma_db")
            )
            graph_path = os.environ.get(
                "CODE_GRAPH_PATH", os.path.join(DATA_DIR, "codebase.graphml")
            )

            logger.info(f"Lazy init - Chroma: {chroma_path}, Graph: {graph_path}")
            _bootstrap_log(f"lazy init starting chroma={chroma_path} graph={graph_path}")

            # Initialize resources
            client = chromadb.PersistentClient(path=chroma_path)
            VECTOR_COLLECTION = client.get_or_create_collection(
                name="codebase_embeddings",
                embedding_function=_get_embedding_function(),
            )
            CODE_GRAPH = nx.read_graphml(graph_path)

            _initialized = True
            logger.info(f"Lazy init complete (graph nodes: {CODE_GRAPH.number_of_nodes()})")
            _bootstrap_log("lazy init complete")
        except Exception as e:
            _init_error = e
            tb = traceback.format_exc()
            logger.critical(f"LAZY INIT ERROR: {e}")
            logger.critical(tb)
            _bootstrap_log(f"LAZY INIT ERROR: {e}\n{tb}")
            raise


@mcp.tool()
def code_semantic_search(query: str, n_results: int = 5) -> str:
    """
    Performs vector similarity search over code snippets.

    Args:
        query: The natural language search query.
        n_results: The number of top results to return.

    Returns:
        A string representation of the search results or an error message.
    """
    try:
        _ensure_initialized()
        results = VECTOR_COLLECTION.query(query_texts=[query], n_results=n_results)
        return str(results)
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return f"Error: {e}"


@mcp.tool()
def code_graph_inspection(function_name: str, dynamic_direction: str = "callers") -> str:
    """
    Traverses the structural dependency call tree using the loaded NetworkX graph.

    Args:
        function_name: The name of the function to inspect.
        dynamic_direction: The direction to traverse ("callers" or "callees").

    Returns:
        A string containing the found structural dependencies or an error message.
    """
    try:
        _ensure_initialized()
        if function_name not in CODE_GRAPH:
            return f"Error: Function '{function_name}' not found."

        if dynamic_direction == "callers":
            relations = list(CODE_GRAPH.predecessors(function_name))
        else:
            relations = list(CODE_GRAPH.successors(function_name))
        return f"Found structural {dynamic_direction} for '{function_name}': {str(relations)}"
    except Exception as e:
        logger.error(f"Graph inspection error: {e}")
        return f"Error: {e}"


async def main():
    """
    Main entry point for starting the MCP server.
    """
    logger.info("Starting MCP server (data loads lazily on first tool call)...")
    _bootstrap_log("starting run_stdio_async")
    try:
        await mcp.run_stdio_async()
        _bootstrap_log("run_stdio_async finished normally")
    except Exception as e:
        _bootstrap_log(f"run_stdio_async CRASHED: {e}\n{traceback.format_exc()}")
        logger.critical(f"run_stdio_async CRASHED: {e}")
        raise


if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
        logger.info("Loop already running, creating task...")
        # If we are in an existing loop (notebook), we need to ensure the task runs
        # and doesn't get immediately cancelled.
        task = loop.create_task(main())
        # We cannot 'await' here directly in the __main__ block if it's already running.
    except RuntimeError:
        logger.info("No loop running, using asyncio.run()...")
        asyncio.run(main())