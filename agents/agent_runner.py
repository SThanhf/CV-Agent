from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
from config.settings import FOUNDRY_PROJECT_ENDPOINT

def run_agent(agent_id: str, user_text: str) -> str:
    project = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint=FOUNDRY_PROJECT_ENDPOINT
    )

    # 1. Create thread
    thread = project.agents.threads.create()

    # 2. Add user message
    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_text
    )

    # 3. Run agent
    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent_id
    )

    if run.status == "failed":
        return f"Run failed: {run.last_error}"

    # 4. Read messages
    messages = project.agents.messages.list(
        thread_id=thread.id,
        order=ListSortOrder.ASCENDING
    )

    for msg in messages:
        if msg.role == "assistant" and msg.text_messages:
            return msg.text_messages[-1].text.value

    return "Agent doesn't return any response."
