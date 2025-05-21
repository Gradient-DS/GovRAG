import json
import os
import time
from langchain_community.vectorstores import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

SCRAPED_DATA_PATH = "/data/scraped.json"
MAX_WAIT_SECONDS = 300 # Wait for 5 minutes max
CHECK_INTERVAL_SECONDS = 5

print(f"Waiting for scraped data file: {SCRAPED_DATA_PATH}")
wait_time = 0
while not os.path.exists(SCRAPED_DATA_PATH) and wait_time < MAX_WAIT_SECONDS:
    print(f"File not found, waiting for {CHECK_INTERVAL_SECONDS}s...")
    time.sleep(CHECK_INTERVAL_SECONDS)
    wait_time += CHECK_INTERVAL_SECONDS

if not os.path.exists(SCRAPED_DATA_PATH):
    print(f"Error: Scraped data file {SCRAPED_DATA_PATH} not found after waiting {MAX_WAIT_SECONDS} seconds.")
    exit(1)

print(f"Found scraped data file: {SCRAPED_DATA_PATH}")

with open(SCRAPED_DATA_PATH) as f:
    raw = json.load(f)

# Ensure 'title' and 'url' are present, providing defaults if not.
# Also ensure 'content' is a string.
processed_docs = []
for i, entry in enumerate(raw):
    content = entry.get("content", "")
    if not isinstance(content, str):
        print(f"Warning: Document {i} content is not a string, converting to string: {content}")
        content = str(content)
    
    metadata = {
        "title": entry.get("title", "N/A"),
        "url": entry.get("url", "N/A"),
        "original_content_preview": content[:200] # Keep a preview for reference
    }
    # Add any other relevant metadata fields from entry if they exist
    for key, value in entry.items():
        if key not in ["content", "title", "url"]: # Avoid duplicating already handled fields
            metadata[key] = value
            
    processed_docs.append(Document(page_content=content, metadata=metadata))


if not processed_docs:
    print("No documents to process after filtering. Exiting.")
    exit(0)

print(f"Embedding {len(processed_docs)} documents...")

qdrant = Qdrant.from_documents(
    processed_docs,
    embedding=HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large"),
    url=os.getenv("QDRANT_URL", "http://qdrant:6333"),
    collection_name="nos_articles",
    force_recreate=True
)

print("Documents embedded and stored in Qdrant successfully.")
