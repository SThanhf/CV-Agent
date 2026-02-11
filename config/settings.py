import os
from dotenv import load_dotenv

load_dotenv()

def env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

FOUNDRY_PROJECT_ENDPOINT = env("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_MODEL_DEPLOYMENT_NAME = env("FOUNDRY_MODEL_DEPLOYMENT_NAME")

AZURE_AI_SEARCH_CONNECTION_NAME = env("AZURE_AI_SEARCH_CONNECTION_NAME")
AI_SEARCH_INDEX_NAME = env("AI_SEARCH_INDEX_NAME")

# For provisioning scripts (optional but recommended)
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY", "")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "")
SEARCH_INDEXER_NAME = os.getenv("SEARCH_INDEXER_NAME", "cv-indexer")
DATA_SOURCE_NAME = os.getenv("DATA_SOURCE_NAME", "cv-data-source")
SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME", "cv-index")