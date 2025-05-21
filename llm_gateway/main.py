import litellm
import uvicorn
import os
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file, especially for local development
# In Docker, these will be passed by docker-compose
load_dotenv()

# Set a default host and port, can be overridden by environment variables
HOST = os.getenv("LLM_GATEWAY_HOST", "0.0.0.0")
PORT = int(os.getenv("LLM_GATEWAY_PORT", "8000"))
CONFIG_FILE_PATH = os.getenv("LITELLM_CONFIG_PATH", "litellm_config.yaml")

# Ensure environment variables for the model are loaded and available for the config
# LiteLLM's config parser will substitute ${VAR_NAME} with environment variables

if __name__ == "__main__":
    print(f"Starting LiteLLM proxy on {HOST}:{PORT}")
    print(f"Loading configuration from: {CONFIG_FILE_PATH}")
    # Check if required env vars for config are present
    if not os.getenv("LLM_GATEWAY_HF_MODEL_ID"):
        print("Warning: LLM_GATEWAY_HF_MODEL_ID environment variable is not set.")
    if not os.getenv("HF_API_KEY"):
        print("Warning: HF_API_KEY environment variable is not set.")

    # LiteLLM's proxy can be started via CLI, but here we use its direct call
    # to integrate with uvicorn for more control if needed in the future.
    # The `litellm.proxy.proxy_server.run_server` is not a standard public API for uvicorn to run directly.
    # The simplest way to run the proxy with a config is often via the CLI command:
    # `litellm --config /path/to/config.yaml --port 8000 --host 0.0.0.0`
    # However, to run it with uvicorn from a Python script, we'd typically wrap it in a FastAPI app
    # or use LiteLLM's built-in server starting mechanism if it supports programmatic start with config.

    # For simplicity with Docker CMD, we will rely on LiteLLM's CLI to start the proxy.
    # This main.py will therefore not be directly run by uvicorn in the Dockerfile CMD.
    # It's here for potential local testing or future expansion.
    # The Dockerfile CMD will directly use: `litellm --config /app/litellm_config.yaml --port 8000 --host 0.0.0.0`
    print("This main.py is a placeholder if not using LiteLLM CLI directly in Docker CMD.")
    print("See Dockerfile for actual server start command.")

    # If you wanted to run programmatically (more complex setup might be needed):
    # from litellm.proxy.proxy_server import app as litellm_app, initialize_proxy_config, load_router_config
    # load_router_config(router=None, config_file_path=CONFIG_FILE_PATH) # This helps load the config
    # initialize_proxy_config(config_file_path=CONFIG_FILE_PATH)
    # uvicorn.run(litellm_app, host=HOST, port=PORT)
