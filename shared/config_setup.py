"""
Handles the complete environment setup for the Codebase Onboarding Agent.

This script defines the `setup_environment_and_models` function, which is the 
single entry point for initializing all necessary components for the agent system.
It performs the following critical tasks:

1. Extracts the Code Knowledge Pack (MCP) archive.
2. Configures the Google API Key from Kaggle Secrets.
3. Initializes the Gemini LLM and Embedding models.
4. Loads the structural code graph (NetworkX).
5. Initializes the ChromaDB client.

The function returns all the critical objects required by the agent factories.
"""
import os
import sys
import warnings
import zipfile
import chromadb
import networkx as nx
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from kaggle_secrets import UserSecretsClient
from google.adk.models.google_llm import Gemini
from google.genai import types

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

def setup_environment_and_models():
    """
    Handles all initial setup: data extraction, API key configuration,
    and initialization of models, clients, and the code graph.
    Returns None for any object that fails to initialize.
    """
    print("🔧 Starting environment and model setup...")

    print("✅ Retry config enabled for HTTP errors:429, 500, 503, 504")

    # --- Configuration ---
    # This section defines the core paths and model names for the agent.

    # Select the Code Knowledge Pack to analyze by uncommenting the desired path.
    # This path points to the .mcp file from the attached Kaggle Dataset.
    
    # 1. For the 'financial_chatbot' repository:
    MCP_ARCHIVE_PATH = "/kaggle/input/datasets/nikhilramaswamy/code-knowledge-pack-agentic-rag-system/financial_chatbot_analysis.mcp"
    
    # 2. For the 'delegator.py' repository:
    # MCP_ARCHIVE_PATH = "/kaggle/input/code-knowledge-pack-delegator-py/delegator.py_analysis.mcp"

    EXTRACT_DESTINATION = "/kaggle/working/mcp_contents"
    CHROMA_DB_PATH = os.path.join(EXTRACT_DESTINATION, "chroma_db")
    GRAPHML_FILE_PATH = os.path.join(EXTRACT_DESTINATION, "codebase.graphml")

    # The primary LLM for the agent's reasoning and planning.
    # gemini-3.1-flash-lite is chosen for its balance of speed and capability.
    LLM_MODEL = "gemini-3.1-flash-lite"

    # The model for generating vector embeddings for semantic search.
    # This must match the model that was used to create the vector store in the MCP file.
    EMBEDDING_MODEL = "gemini-embedding-001"

    # --- Setup: Extract MCP Archive ---
    if not os.path.exists(EXTRACT_DESTINATION):
        print(f"Extracting MCP archive from {MCP_ARCHIVE_PATH}...")
        try:
            with zipfile.ZipFile(MCP_ARCHIVE_PATH, 'r') as zip_ref:
                zip_ref.extractall(EXTRACT_DESTINATION)
            print(f"✅ Successfully extracted to {EXTRACT_DESTINATION}")
        except Exception as e:
            print(f"❌ ERROR: Failed to extract MCP archive: {e}. Please check if MCP_ARCHIVE_PATH correctly points to the .mcp file of the attached kaggle dataset")
            return None, None, None, None
    else:
        print("✅ MCP contents already exist.")

    # --- API Key Handling ---
    try:
        user_secrets = UserSecretsClient()
        GOOGLE_API_KEY = user_secrets.get_secret("GOOGLE_API_KEY")
        os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
        print("✅ GOOGLE_API_KEY has been set.")
    except Exception as e:
        print(f"❌ ERROR: Could not retrieve Kaggle secret 'GOOGLE_API_KEY'. {e}")
        return None, None, None, None

    # --- Model and Client Initialization ---
    try:
        embedding_model = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=GOOGLE_API_KEY)
        langchain_llm = ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=GOOGLE_API_KEY)
        adk_model = Gemini(llm=langchain_llm, retry_options=retry_config)
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        print("✅ Models and clients initialized.")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize models or ChromaDB client. {e}")
        return None, None, None, None

    # --- Graph Loading ---
    try:
        code_graph = nx.read_graphml(GRAPHML_FILE_PATH)
        print("✅ Code graph loaded.")
    except Exception as e:
        print(f"❌ ERROR: An error occurred while loading the graph: {e}")
        return adk_model, chroma_client, embedding_model, None
    
    return adk_model, chroma_client, embedding_model, code_graph

if __name__ == '__main__':
    try:
        adk_model, chroma_client, embedding_model, code_graph = setup_environment_and_models()
        print("\n✅ config_setup.py ran successfully.")
    except SystemExit:
        print("\n❌ config_setup.py failed due to errors.")