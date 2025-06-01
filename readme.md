_Public_
## RAG setup for Government compliant applications
GovRAG is a minimal setup (POC) for governmental RAG applications, utilizing MCP protocol, QDrant, open webui and litellm. 

## Project Structure

```
.
├── .gitmodules
├── docker-compose.yaml
├── embedding
│   ├── Dockerfile
│   └── embed_and_store.py
├── llm_gateway
│   ├── Dockerfile
│   └── litellm_config.yaml
├── mcp
│   └── mcp-nos
│       ├── Dockerfile
│       └── main.py
├── openwebui
│   └── (git submodule)
├── qdrant_storage
│   └── (data will be stored here)
├── readme.md
└── scraper
    ├── Dockerfile
    └── run_all.py
```

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone --recurse-submodules <repository-url>
    cd <repository-name>
    ```
    The `--recurse-submodules` flag is important to initialize and update the `openwebui` submodule. If you have already cloned the repository without this flag, you can initialize the submodules by running:
    ```bash
    git submodule update --init --recursive
    ```
2.  **Set up your Hugging Face API Key:**
    You will need a Hugging Face API key with permissions to access the following models:
    *   `meta-llama/Meta-Llama-3-70B-Instruct`
    *   `google/gemma-1.1-2b-it` (Note: the compose file currently lists `HF_GEMMA_3_27B` which seems like a typo, updated to a valid Gemma model)
    *   `Qwen/Qwen1.5-72B-Chat` (Note: the compose file currently lists `HF_QWEN_3_235B`, updated to a valid Qwen model)

    Create a `.env` file in the root of the project and add your API key:
    ```env
    HF_API_KEY="your_hf_api_key_here"
    HF_LLAMA_70B=huggingface/meta-llama/Llama-3.3-70B-Instruct
    HF_QWEN_3_235B=huggingface/Qwen/Qwen3-235B-A22B
    ```
3.  **Run Docker Compose:**
    ```bash
    docker-compose up -d
    ```
    This command will build the images and start all the services in detached mode.

## What Happens When You Run `docker-compose up`

The `docker-compose.yaml` file defines and orchestrates several services:

*   **`qdrant`**: A vector database used to store embeddings of your data. Data is persisted in the `./qdrant_storage` volume.
*   **`scraper`**: This service (defined in the `scraper` directory) is responsible for fetching data. Its `run_all.py` script will be executed. The scraped data is stored in a shared volume named `scraped_data_volume`.
*   **`embedding`**: This service (defined in the `embedding` directory) takes the data from the `scraped_data_volume` (produced by the `scraper`), generates embeddings using a sentence transformer model, and stores them in the `qdrant` database. This service depends on the `scraper` and `qdrant` services.
*   **`mcp-nos`**: This service (defined in `mcp/mcp-nos`) likely implements the Model Component Protocol (MCP) for Networked Operating Systems (NOS). It acts as a backend service that OpenWebUI can connect to.
*   **`llm_gateway`**: This service (defined in `llm_gateway`) uses LiteLLM to provide a unified API gateway to various Large Language Models. It's configured via `litellm_config.yaml` and uses the Hugging Face API keys and model names defined in your `.env` file and passed as environment variables. The currently configured models are:
    *   **Llama 3 70B Instruct (`meta-llama/Llama-3.3-70B-Instruct`)**: A large, instruction-tuned model from Meta.
    *   **Qwen 3 235B (`huggingface/Qwen/Qwen3-235B-A22B`)**: A large chat model from Alibaba Cloud.
    You need to ensure your Hugging Face API key has the necessary permissions to access these specific model repositories.
*   **`openwebui`**: This service (from the `openwebui` submodule) provides a user-friendly chat interface similar to ChatGPT. It's configured to use the `llm_gateway` as its OpenAI-compatible API endpoint.

## Accessing the Web UI and Configuring MCP

Once all services are running:

1.  Open your web browser and navigate to `http://localhost:3000`. This is where OpenWebUI is running.
2.  To enable the MCP functionality (e.g., for retrieval augmented generation or other custom tools):
    *   In OpenWebUI, navigate to **Settings**.
    *   Go to the **Tools** section.
    *   Click the **+** button to add a new tool.
    *   Enter `http://localhost:8001` as the endpoint for the NOS MCP service. (This is the address of the `mcp-nos` service as seen from your host machine, though internally OpenWebUI will use `http://mcp-nos:8001`).

Now you should be able to interact with the language models and utilize any RAG capabilities exposed via the MCP service.

