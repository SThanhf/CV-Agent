import sys
from pathlib import Path

# Fix import when running from scripts/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import os
import logging
from datetime import timedelta

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    AzureOpenAIEmbeddingSkill,
    HnswAlgorithmConfiguration,
    HnswParameters,
    IndexingSchedule,
    IndexProjectionMode,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    SearchIndexerSkillset,
    SimpleField,
    SplitSkill,
    VectorSearch,
    VectorSearchProfile,
    DocumentExtractionSkill,
)

from config.settings import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
    AZURE_STORAGE_CONNECTION_STRING,
    BLOB_CONTAINER_NAME,
    SEARCH_INDEXER_NAME,
    DATA_SOURCE_NAME,
    SEARCH_INDEX_NAME,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# =========================
# Embedding config (env)
# =========================
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_OPENAI_EMBEDDING_DIM = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIM", "1536"))

if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_EMBEDDING_DEPLOYMENT]):
    raise RuntimeError(
        "Missing env vars: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    )

SKILLSET_NAME = "cv-skillset" 

# =========================
# CHUNK INDEX SCHEMA
# =========================
CHUNK_INDEX_SCHEMA = SearchIndex(
    name=SEARCH_INDEX_NAME,
    fields=[
        # chunk id
        SearchField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
            analyzer_name="keyword",
        ),

        # parent document id (Azure projection sẽ set theo parent_key_field_name)
        SimpleField(
            name="document_id",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        # candidate_id = filename (metadata_storage_name)
        SimpleField(
            name="candidate_id",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True,
        ),

        # chunk text
        SearchableField(
            name="text",
            type=SearchFieldDataType.String,
            analyzer_name="en.lucene",
        ),

        # vector embedding
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=AZURE_OPENAI_EMBEDDING_DIM,
            vector_search_profile_name="vs-default",
        ),
    ],
    vector_search=VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-cosine",
                parameters=HnswParameters(
                    metric="cosine", m=16, ef_construction=400, ef_search=100
                ),
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="vs-default",
                algorithm_configuration_name="hnsw-cosine",
            )
        ],
    ),
)

# =========================
# DATA SOURCE (using blob)
# =========================
DATA_SOURCE = SearchIndexerDataSourceConnection(
    name=DATA_SOURCE_NAME,
    type="azureblob",
    connection_string=AZURE_STORAGE_CONNECTION_STRING,
    container=SearchIndexerDataContainer(name=BLOB_CONTAINER_NAME),
)

# =========================
# SKILLSET (split skill + embedding skill + index projection)
# =========================
SKILLSET = SearchIndexerSkillset(
    name=SKILLSET_NAME,
    skills=[
        DocumentExtractionSkill(
            context="/document",  # apply to whole document
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="extractedContent", target_name="extractedContent")],
        ),
        SplitSkill(
            context="/document",
            text_split_mode="pages",
            maximum_page_length=1400,    # 
            page_overlap_length=350,     #
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="textItems", target_name="pages")],
        ),
        AzureOpenAIEmbeddingSkill(
            context="/document/pages/*",
            resource_url=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            deployment_name=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            model_name=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            dimensions=AZURE_OPENAI_EMBEDDING_DIM,
            inputs=[InputFieldMappingEntry(name="text", source="/document/pages/*")],
            outputs=[OutputFieldMappingEntry(name="embedding", target_name="embedding")],
        ),
    ],
    index_projection=SearchIndexerIndexProjection(
        selectors=[
            SearchIndexerIndexProjectionSelector(
                target_index_name=SEARCH_INDEX_NAME,
                parent_key_field_name="document_id",
                source_context="/document/pages/*",
                mappings=[
                    InputFieldMappingEntry(name="text", source="/document/pages/*"),
                    InputFieldMappingEntry(name="embedding", source="/document/pages/*/embedding"),

                    # map filename -> candidate_id
                    InputFieldMappingEntry(
                        name="candidate_id",
                        source="/document/metadata_storage_name",
                    ),
                ],
            )
        ],
        parameters=SearchIndexerIndexProjectionsParameters(
            projection_mode=IndexProjectionMode.INCLUDE_INDEXING_PARENT_DOCUMENTS
        ),
    ),
)

# =========================
# INDEXER
# =========================
INDEXER = SearchIndexer(
    name=SEARCH_INDEXER_NAME,
    data_source_name=DATA_SOURCE_NAME,
    target_index_name=SEARCH_INDEX_NAME,  # using 1 index for chunks
    skillset_name=SKILLSET.name,
    schedule=IndexingSchedule(interval=timedelta(days=1)),
)

def setup_search():
    if not AZURE_SEARCH_ENDPOINT or not AZURE_SEARCH_ADMIN_KEY:
        raise RuntimeError("Missing AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_ADMIN_KEY in env")

    index_client = SearchIndexClient(
        AZURE_SEARCH_ENDPOINT,
        AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY),
    )
    indexer_client = SearchIndexerClient(
        AZURE_SEARCH_ENDPOINT,
        AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY),
    )

    # 1) Index
    try:
        index_client.get_index(SEARCH_INDEX_NAME)
        # logger.info("Index exists: %s", SEARCH_INDEX_NAME)
    except HttpResponseError:
        # logger.info("Creating index: %s", SEARCH_INDEX_NAME)
        index_client.create_index(CHUNK_INDEX_SCHEMA)

    # 2) Data source
    try:
        indexer_client.get_data_source_connection(DATA_SOURCE_NAME)
        # logger.info("Data source exists: %s", DATA_SOURCE_NAME)
    except HttpResponseError:
        # logger.info("Creating data source: %s", DATA_SOURCE_NAME)
        indexer_client.create_data_source_connection(DATA_SOURCE)

    # 3) Skillset
    try:
        indexer_client.get_skillset(SKILLSET.name)
        # logger.info("Skillset exists: %s", SKILLSET.name)
    except HttpResponseError:
        # logger.info("Creating skillset: %s", SKILLSET.name)
        indexer_client.create_skillset(SKILLSET)

    # 4) Indexer
    try:
        indexer_client.get_indexer(SEARCH_INDEXER_NAME)
        # logger.info("Indexer exists: %s", SEARCH_INDEXER_NAME)
    except HttpResponseError:
        # logger.info("Creating indexer: %s", SEARCH_INDEXER_NAME)
        indexer_client.create_indexer(INDEXER)

    # logger.info("Azure AI Search setup completed")

if __name__ == "__main__":
    setup_search()
