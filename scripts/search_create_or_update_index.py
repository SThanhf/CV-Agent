import sys
from pathlib import Path

# Add project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)

from config.settings import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
)

# CV SEARCH INDEX
INDEX_NAME = "cv-index-chunks"

# Default embedding dimension for text-embedding-3-small
EMBEDDING_DIMENSIONS = 1536  # text-embedding-3-small

def main():
    client = SearchIndexClient(
        AZURE_SEARCH_ENDPOINT,
        AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
    )

    index = SearchIndex(
        name=INDEX_NAME,
        fields=[
            # ID của từng chunk
            SimpleField(
                name="id",
                type="Edm.String",
                key=True
            ),

            # Text chunk từ CV
            SearchableField(
                name="text",
                type="Edm.String",
                analyzer_name="standard.lucene"
            ),

            # Vector embedding
            SearchableField(
                name="embedding",
                type="Collection(Edm.Single)",
                vector_search_dimensions=EMBEDDING_DIMENSIONS,
                vector_search_profile_name="vector-profile"
            ),

            # ID document cha (CV gốc)
            SimpleField(
                name="document_id",
                type="Edm.String",
                filterable=True
            ),
        ],
        vector_search=VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="hnsw"
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="vector-profile",
                    algorithm_configuration_name="hnsw"
                )
            ]
        )
    )

    client.create_index(index)
    print("✅ Index CREATED:", INDEX_NAME)

if __name__ == "__main__":
    main()
