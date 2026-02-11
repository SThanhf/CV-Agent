import sys
from pathlib import Path

# Add project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import SearchIndexer

from config.settings import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
    DATA_SOURCE_NAME,
)

# SETUP INDEXER
INDEXER_NAME = "cv-indexer"
SKILLSET_NAME = "cv-skillset"
TARGET_INDEX_NAME = "cv-index-chunks"

def main():
    client = SearchIndexerClient(
        AZURE_SEARCH_ENDPOINT,
        AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
    )

    indexer = SearchIndexer(
        name=INDEXER_NAME,
        data_source_name=DATA_SOURCE_NAME,
        target_index_name=TARGET_INDEX_NAME,
        skillset_name=SKILLSET_NAME,
    )

    client.create_or_update_indexer(indexer)
    print("Indexer CREATED/UPDATED:", INDEXER_NAME) #print indexer created or updated

if __name__ == "__main__":
    main()
