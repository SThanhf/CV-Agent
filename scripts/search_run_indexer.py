import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from config.settings import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
    SEARCH_INDEXER_NAME,
)

def main():
    client = SearchIndexerClient(
        AZURE_SEARCH_ENDPOINT,
        AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
    )

    client.run_indexer(SEARCH_INDEXER_NAME)
    print(f"Indexer '{SEARCH_INDEXER_NAME}' started")

if __name__ == "__main__":
    main()
