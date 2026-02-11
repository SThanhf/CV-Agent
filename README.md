# CV Agent (Foundry Agent SDK + Azure AI Search)

## 1) Setup
- Python 3.10+
- `pip install -r requirements.txt`
- Create `.env` from template and fill keys, values and connections.

## 2) Foundry connection to Azure AI Search
In Foundry portal:
Management center -> Connected resources -> Add connection -> Azure AI Search
Set `AZURE_AI_SEARCH_CONNECTION_NAME` in `.env`.

## 3) Provision Search pipeline from Blob
python scripts/setup_search.py
python scripts/search_run_indexer.py

## 4) Run UI
streamlit run app.py
