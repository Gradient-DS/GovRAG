FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY embed_and_store.py .

# Input directory for scraped data, to be mounted as a volume
# The script embed_and_store.py expects data in /data/scraped.json
# So the volume should be mounted to /data in docker-compose.yaml

CMD ["python", "embed_and_store.py"] 