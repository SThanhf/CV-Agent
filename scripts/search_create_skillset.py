import requests
import json
from config.settings import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_ADMIN_KEY,
)

SKILLSET_NAME = "cv-skillset"

url = f"{AZURE_SEARCH_ENDPOINT}/skillsets/{SKILLSET_NAME}?api-version=2023-11-01"

headers = {
    "Content-Type": "application/json",
    "api-key": AZURE_SEARCH_ADMIN_KEY,
}

skillset_payload = {
  "name": SKILLSET_NAME,
  "skills": [
    {
      "@odata.type": "#Microsoft.Skills.Text.SplitSkill",
      "name": "#1",
      "context": "/document",
      "defaultLanguageCode": "en",
      "textSplitMode": "pages",
      "maximumPageLength": 1400,
      "pageOverlapLength": 350,
      "maximumPagesToTake": 0,
      "unit": "characters",
      "inputs": [
        {
          "name": "text",
          "source": "/document/content"
        }
      ],
      "outputs": [
        {
          "name": "textItems",
          "targetName": "pages"
        }
      ]
    },
    {
      "@odata.type": "#Microsoft.Skills.Text.AzureOpenAIEmbeddingSkill",
      "name": "#2",
      "context": "/document/pages/*",
      "resourceUri": "https://foundryrss1.openai.azure.com",
      "deploymentId": "text-embedding-3-small",
      "dimensions": 1536,
      "modelName": "text-embedding-3-small",
      "inputs": [
        {
          "name": "text",
          "source": "/document/pages/*"
        }
      ],
      "outputs": [
        {
          "name": "embedding",
          "targetName": "embedding"
        }
      ]
    }
  ],
  "indexProjections": {
    "selectors": [
      {
        "targetIndexName": "cv-index-chunks",
        "parentKeyFieldName": "document_id",
        "sourceContext": "/document/pages/*",
        "mappings": [
          {
            "name": "text",
            "source": "/document/pages/*"
          },
          {
            "name": "embedding",
            "source": "/document/pages/*/embedding"
          }
        ]
      }
    ],
    "parameters": {
      "projectionMode": "includeIndexingParentDocuments"
    }
  }
}

response = requests.put(url, headers=headers, data=json.dumps(skillset_payload))

# Check response
if response.status_code not in (200, 201):
    print("Failed to create skillset")
    print(response.status_code, response.text)
else:
    print("Skillset created EXACTLY as portal JSON")
