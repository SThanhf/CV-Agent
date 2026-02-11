from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from config.settings import FOUNDRY_PROJECT_ENDPOINT, AZURE_AI_SEARCH_CONNECTION_NAME

def get_ai_search_connection_id() -> str:
    """
    Returns the project connection resource id for Azure AI Search.
    Foundry docs: lookup connection by name via AIProjectClient.connections.get(name). :contentReference[oaicite:3]{index=3}
    """
    with DefaultAzureCredential() as cred, AIProjectClient(endpoint=FOUNDRY_PROJECT_ENDPOINT, credential=cred) as project:
        conn = project.connections.get(AZURE_AI_SEARCH_CONNECTION_NAME)
        return conn.id
