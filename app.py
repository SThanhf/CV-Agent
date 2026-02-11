import os
import streamlit as st
from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

# =========================
# ENV
# =========================
load_dotenv()

FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_AGENT_ID = os.getenv("FOUNDRY_AGENT_ID")

if not FOUNDRY_PROJECT_ENDPOINT or not FOUNDRY_AGENT_ID:
    st.error("Missing FOUNDRY_PROJECT_ENDPOINT or FOUNDRY_AGENT_ID in .env")
    st.stop()

# =========================
# STREAMLIT CONFIG
# =========================
st.set_page_config(
    page_title="CV Chat Agent",
    page_icon="💬",
    layout="wide"
)

st.title("💬 CV Chat Agent")
st.caption("Chat với CV Agent (Azure AI Search + Foundry Agent)")

# =========================
# INIT CLIENT
# =========================
project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=FOUNDRY_PROJECT_ENDPOINT
)

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    # TẠO THREAD DUY NHẤT
    thread = project.agents.threads.create()
    st.session_state.thread_id = thread.id

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("### ⚙️ Tuỳ chọn")
    # if st.button("🔄 Reset cuộc trò chuyện"):
    #     st.session_state.messages = []
    #     thread = project.agents.threads.create()
    #     st.session_state.thread_id = thread.id
    #     st.experimental_rerun()

# =========================
# RENDER CHAT HISTORY
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# USER INPUT
# =========================
prompt = st.chat_input("Nhập câu hỏi về CV...")

##add context to prompt##
enhanced_prompt = f"""
You are evaluating candidate suitability for a specific job description.

Job Description:
{prompt}

TASKS (FOLLOW STRICTLY IN ORDER):

1. Extract the key requirements from the Job Description, including:
   - Required role
   - Required skills/technologies
   - Required years of experience
   - Industry/domain requirements

2. Review the candidate CV retrieved from the system.
   - Use ONLY information explicitly stated in the CV.
   - Do NOT infer or assume missing experience.

3. Compare the CV against EACH job requirement.

4. Determine whether the candidate is:
   - Suitable
   - Partially suitable
   - Not suitable

RESPONSE FORMAT (MANDATORY, DO NOT ADD EXTRA TEXT):

Job Requirements:
- Role:
- Skills:
- Experience:
- Industry:

Candidate Evaluation:
- Name:
- Current background summary (FACTUAL ONLY):

Requirement Match:
- Role match:
- Skill match:
- Experience match:
- Industry match:

Missing or Weak Requirements:
- ...

Overall Suitability:
- Suitability level: Suitable / Partially suitable / Not suitable
- Justification (1–2 factual sentences only)

"""

if prompt:
    # Lưu & hiển thị user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Gửi message vào THREAD HIỆN TẠI
    project.agents.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=enhanced_prompt
    )

    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent are analyzing CVs..."):
            try:
                run = project.agents.runs.create_and_process(
                    thread_id=st.session_state.thread_id,
                    agent_id=FOUNDRY_AGENT_ID
                )

                if run.status == "failed":
                    answer = f"Agent failed: {run.last_error}"
                else:
                    messages = project.agents.messages.list(
                        thread_id=st.session_state.thread_id,
                        order=ListSortOrder.ASCENDING
                    )

                    answer = "Agent can't response."
                    for m in messages:
                        if m.role == "assistant" and m.text_messages:
                            answer = m.text_messages[-1].text.value

                st.markdown(answer)

                # Lưu assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                error_msg = f"Error when calling agent: {e}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
