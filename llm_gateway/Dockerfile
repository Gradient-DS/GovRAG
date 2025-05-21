FROM python:3.9-slim-bookworm

WORKDIR /app

# Install build-essential for potential native dependencies if any
# RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from the llm_gateway directory (the build context) to /app
COPY . .

# Expose the port LiteLLM will run on (defaulting to 8000 for the gateway)
EXPOSE 8000

# Command to run LiteLLM proxy with the configuration
# It will pick up LLM_GATEWAY_HF_MODEL_ID and HF_API_KEY from environment variables passed by docker-compose
# Added echo commands for debugging environment variables
CMD ["sh", "-c", "echo Seeing LLM_GATEWAY_HF_MODEL_ID: $LLM_GATEWAY_HF_MODEL_ID && echo Seeing HF_API_KEY: $HF_API_KEY && litellm --config /app/litellm_config.yaml --port 8000 --host 0.0.0.0 --debug"] 