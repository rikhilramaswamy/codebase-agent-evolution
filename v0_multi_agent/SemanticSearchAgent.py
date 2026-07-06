"""
Defines the SemanticSearchAgent and its associated tools.

This agent acts as the "semantic expert" in the multi-agent system. It is 
responsible for finding relevant code snippets from a vector database based on 
natural language queries. 
"""

from google.adk.agents import LlmAgent

# Global state for dependencies, to be set by the AgentDriver
_chroma_client = None
_embedding_model = None

def set_dependencies(chroma_client, embedding_model):
    """Sets the dependencies required for semantic search."""
    global _chroma_client, _embedding_model
    _chroma_client = chroma_client
    _embedding_model = embedding_model

# --- Custom Tool Definition (Simple Function) ---
def find_relevant_code(query: str, n_results: int = 3) -> str:
    """
    Finds code snippets semantically relevant to a natural language query.

    Args:
        query: A natural language description of what code to find.
        n_results: Number of code snippets to return (default: 3).

    Returns:
        A formatted string containing the relevant code snippets.
    """
    if _chroma_client is None or _embedding_model is None:
        return "Search dependencies (chroma_client or embedding_model) are not initialized."

    CHROMA_COLLECTION_NAME = "codebase_embeddings" 
    try:
        collection = _chroma_client.get_collection(name=CHROMA_COLLECTION_NAME)
        query_embedding = _embedding_model.embed_query(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=n_results)

        if not results or not results.get('documents') or not results['documents'][0]:
            return "No relevant code snippets found."

        formatted_snippets = [f"--- Snippet {i+1} ---\n{doc}\n" for i, doc in enumerate(results['documents'][0])]
        return "\n".join(formatted_snippets)
    except Exception as e:
        return f"An error occurred while searching: {e}"

# --- Semantic Search Agent Definition ---
# Note: adk_model will be passed during initialization from AgentDriver
def build_semantic_search_agent(adk_model):
    return LlmAgent(
        name="SemanticSearchAgent",
        model=adk_model,
        instruction=(
            "You are an expert code search assistant. Your job is to use the "
            "`find_relevant_code` tool to find code snippets that answer a user's "
            "question about a codebase. Only use the provided tool."
        ),
        tools=[find_relevant_code]
    )