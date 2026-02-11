import sys
from pathlib import Path

# Add project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
)

from config.settings import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
    AZURE_STORAGE_CONNECTION_STRING,
    BLOB_CONTAINER_NAME,
)

# CV DATA SOURCE
DATA_SOURCE_NAME = "cv-data-source"

def main():
    client = SearchIndexerClient(
        AZURE_SEARCH_ENDPOINT,
        AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
    )

    container = SearchIndexerDataContainer(
        name=BLOB_CONTAINER_NAME
    )

    data_source = SearchIndexerDataSourceConnection(
        name=DATA_SOURCE_NAME,
        type="azureblob",
        connection_string=AZURE_STORAGE_CONNECTION_STRING,
        container=container,
        description="CV PDF/DOCX stored in Azure Blob Storage"
    )

    client.create_or_update_data_source_connection(data_source)
    print("✅ Data source CREATED/UPDATED:", DATA_SOURCE_NAME)

if __name__ == "__main__":
    main()
