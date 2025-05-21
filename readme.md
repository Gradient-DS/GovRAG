## RAG setup for Government compliant applications
This is the first attempt at building a POC for governmental RAG applications, utilizing MCP protocol, QDrant, langchain, open webui and as much efficient code as possible.

## Initial structure
GOVRAG/
├── docker-compose.yml
├── openwebui/                 # Git submodule (editable frontend)
├── rag_api/                   # FastAPI + LangChain backend
│   ├── app.py
│   ├── chains.py
│   ├── tools.py
│   ├── config.py
│   └── requirements.txt
├── embedding/
│   └── embed_and_store.py
├── scraper/
│   └── run_all.py
└── llm_gateway/               # Optional: LLM API proxy
    └── main.py