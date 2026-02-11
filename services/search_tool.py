from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType
from config.settings import AI_SEARCH_INDEX_NAME
from services.foundry_connections import get_ai_search_connection_id

def build_ai_search_tool():
    """
    AzureAISearchTool requires index_connection_id (project connection id) + index_name. :contentReference[oaicite:4]{index=4}
    """
    conn_id = get_ai_search_connection_id()
    return AzureAISearchTool(
        index_connection_id=conn_id,
        index_name=AI_SEARCH_INDEX_NAME,
        query_type=AzureAISearchQueryType.VECTOR_SEMANTIC_HYBRID,
        top_k=5,
        filter="",
    )
