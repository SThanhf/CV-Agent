# CV Agent (Foundry Agent SDK + Azure AI Search)
CV Agent is an agent developed for CV analysis and HR supporter, is built by Azure AI search service and Agent in Azure AI Foundry.

# Project Structure
```
CV-Agent/
├── agents/      # Agent connection
├── config/      # Connection settings
├── scripts/     # Azure AI search datasource, index, skillset and indexer setup
├── services/    # Services setup
├── app.py       # Streamlit frontend
├── requirements.txt
└── README.md
```

--- 
## 1) Prerequisites
- Python 3.10+
- Download package requirements through pip
- Create `.env` from template and fill keys, values and connections.
- Azure Supcription with: 
    + Azure AI Search
    + Azure AI Service with text embedding model
    + Azure Blob Storage
    + A Azure AI Foundry agent with agent-supported model, is connected to AI Search knowledge

- Foundry connection to Azure AI Search
    + In Foundry portal: Management center -> Connected resources -> Add connection -> Azure AI Search
    + Set `AZURE_AI_SEARCH_CONNECTION_NAME` in `.env`.

## 2) Provision Search pipeline from Blob
python scripts/setup_search.py
python scripts/search_run_indexer.py

## 3) Run UI
streamlit run app.py