FROM python:3.9-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "litellm --config /app/litellm_config.yaml --port 8000 --host 0.0.0.0 --debug"] 