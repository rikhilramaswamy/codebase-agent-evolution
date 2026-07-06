"""
Performs semantic search over a codebase using ChromaDB vector embeddings.

This script acts as a standalone skill for the agent, allowing it to retrieve
relevant code snippets based on natural language queries. It expects the
database path and API key to be provided via environment variables.
"""
import argparse
import json
import os
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from chromadb import EmbeddingFunction, Documents, Embeddings

def main():
    """
    Parses command-line arguments, initializes the ChromaDB client, and 
    performs a semantic search against the codebase embeddings.
    """
    parser = argparse.ArgumentParser(description="Semantic code search skill.")
    parser.add_argument("--query", type=str, required=True, help="Natural language query.")
    parser.add_argument("--n_results", type=int, default=3, help="Number of results to return.")
    args = parser.parse_args()

    # Access persisted chroma client
    db_path = os.environ.get("CHROMA_DB_PATH", "./chroma_db")
    client = chromadb.PersistentClient(path=db_path)
    
    # Initialize the correct embedding model to match collection (3072 dims)
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001", 
        google_api_key=os.environ.get("GOOGLE_API_KEY")
    )
    
    # Fully compliant EmbeddingFunction
    class LangchainEmbeddingFunction(EmbeddingFunction):
        """
        Adapts the LangChain embedding model to the ChromaDB EmbeddingFunction interface.
        """
        def __call__(self, input: Documents) -> Embeddings:
            return embedding_model.embed_documents(input)

    collection_name = "codebase_embeddings"
    collection = client.get_collection(
        name=collection_name,
        embedding_function=LangchainEmbeddingFunction()
    )
    
    results = collection.query(
        query_texts=[args.query],
        n_results=args.n_results
    )
    
    print(json.dumps({"results": results}))

if __name__ == "__main__":
    main()
