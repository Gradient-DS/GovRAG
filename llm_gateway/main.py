'''
This file is a placeholder for the LiteLLM proxy.
It's not used in the Dockerfile CMD.
It's here for potential local testing or future expansion.
'''

import litellm
import uvicorn
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("LLM_GATEWAY_HOST", "0.0.0.0")
PORT = int(os.getenv("LLM_GATEWAY_PORT", "8000"))
CONFIG_FILE_PATH = os.getenv("LITELLM_CONFIG_PATH", "litellm_config.yaml")

if __name__ == "__main__":
    print(f"Starting LiteLLM proxy on {HOST}:{PORT}")
    print(f"Loading configuration from: {CONFIG_FILE_PATH}")
    if not os.getenv("LLM_GATEWAY_HF_MODEL_ID"):
        print("Warning: LLM_GATEWAY_HF_MODEL_ID environment variable is not set.")
    if not os.getenv("HF_API_KEY"):
        print("Warning: HF_API_KEY environment variable is not set.")
    print("This main.py is a placeholder if not using LiteLLM CLI directly in Docker CMD.")
    print("See Dockerfile for actual server start command.")
