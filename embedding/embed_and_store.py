import json
import os
import time
from langchain_community.vectorstores import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# SCRAPED_DATA_PATH = "/data/scraped.json" # Old path
DATA_DIR = "/app/data" # Directory where scraped JSON files are stored
# Files like scraped_nos.json, scraped_nu.json are expected here

MAX_WAIT_SECONDS = 300 # Wait for 5 minutes max
CHECK_INTERVAL_SECONDS = 5

# QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333") # Defined later per collection
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"

def get_scraped_files_info(data_dir):
    """
    Identifies scraped JSON files and derives collection names.
    Returns a list of dicts: [{"path": file_path, "collection": collection_name, "source_name": source_name}]
    Example: [{"path": "/app/data/scraped_nos.json", "collection": "nos_articles", "source_name": "nos"},
              {"path": "/app/data/scraped_nu.json", "collection": "nu_articles", "source_name": "nu"}]
    """
    files_info = []
    if not os.path.isdir(data_dir):
        print(f"Error: Data directory {data_dir} not found.")
        return files_info

    for filename in os.listdir(data_dir):
        if filename.startswith("scraped_") and filename.endswith(".json"):
            file_path = os.path.join(data_dir, filename)
            # Derive collection name from filename, e.g., "scraped_nos.json" -> "nos_articles"
            source_name = filename.replace("scraped_", "").replace(".json", "")
            collection_name = f"{source_name}_articles"
            files_info.append({"path": file_path, "collection": collection_name, "source_name": source_name})
    return files_info

def wait_for_files(files_to_check_info):
    """Waits for all specified files to exist."""
    all_files_found = False
    total_wait_time = 0

    while not all_files_found and total_wait_time < MAX_WAIT_SECONDS:
        found_all_currently = True
        for file_info in files_to_check_info:
            if not os.path.exists(file_info["path"]):
                print(f"File {file_info['path']} not found, waiting...")
                found_all_currently = False
                break
        
        if found_all_currently:
            all_files_found = True
            print("All required scraped data files found.")
            break
        else:
            time.sleep(CHECK_INTERVAL_SECONDS)
            total_wait_time += CHECK_INTERVAL_SECONDS
            if total_wait_time >= MAX_WAIT_SECONDS:
                print(f"Error: Not all scraped data files found after waiting {MAX_WAIT_SECONDS} seconds.")
                # Identify missing files
                missing_files = [info["path"] for info in files_to_check_info if not os.path.exists(info["path"])]
                print(f"Missing files: {missing_files}")
                exit(1) # Exit if files are not found after waiting
    return all_files_found


def process_and_embed_data(file_path, collection_name, source_name):
    print(f"\n--- Processing data for {source_name} from {file_path} ---")
    print(f"Target Qdrant collection: {collection_name}")

    if not os.path.exists(file_path):
        print(f"Error: Scraped data file {file_path} not found.")
        return # Skip this file if it doesn't exist

    print(f"Found scraped data file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return # Skip if JSON is invalid
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return


    if not raw:
        print(f"No data found in {file_path}. Skipping embedding for this source.")
        return

    processed_docs = []
    for i, entry in enumerate(raw):
        content = entry.get("content", "")
        if not isinstance(content, str):
            print(f"Warning: Document {i} from {source_name} content is not a string, converting: {str(content)[:50]}...")
            content = str(content)
        
        metadata = {
            "title": entry.get("title", "N/A"),
            "url": entry.get("url", "N/A"),
            "source": entry.get("source", source_name), # Ensure source is in metadata
            "original_content_preview": content[:200]
        }
        for key, value in entry.items():
            if key not in ["content", "title", "url", "source"]: # Avoid duplicating already handled fields
                metadata[key] = value
                
        processed_docs.append(Document(page_content=content, metadata=metadata))

    if not processed_docs:
        print(f"No documents to process for {source_name} after initial processing. Skipping for this source.")
        return

    print(f"Embedding {len(processed_docs)} documents from {source_name} into collection '{collection_name}'...")

    qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333") # Get Qdrant URL
    
    try:
        qdrant = Qdrant.from_documents(
            processed_docs,
            embedding=HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL),
            url=qdrant_url,
            collection_name=collection_name,
            force_recreate=True # Recreate the collection each time for this script's purpose
        )
        print(f"Documents from {source_name} embedded and stored in Qdrant collection '{collection_name}' successfully.")
    except Exception as e:
        print(f"Error embedding documents for {source_name} into {collection_name}: {e}")
        print(f"Make sure your Qdrant instance is running and accessible at {qdrant_url}.")


if __name__ == "__main__":
    print(f"Looking for scraped data files in: {DATA_DIR}")
    
    # Define which sources we expect data from. This should align with SITES_CONFIG in scraper.
    expected_sources_config = {
        "nos": {"output_filename": "scraped_nos.json", "collection_name": "nos_articles"},
        "nu":  {"output_filename": "scraped_nu.json", "collection_name": "nu_articles"}
    }
    
    files_to_process_info = []
    for src_key, src_info in expected_sources_config.items():
        files_to_process_info.append({
            "path": os.path.join(DATA_DIR, src_info["output_filename"]),
            "collection": src_info["collection_name"],
            "source_name": src_key
        })

    if not files_to_process_info:
        print("No data files configured to process based on expected_sources_config. Exiting.")
        exit(0)
    
    print("Expected data files to process:")
    for info in files_to_process_info:
        print(f"  - Path: {info['path']}, Collection: {info['collection']}")

    if wait_for_files(files_to_process_info): # wait_for_files will exit if not all found
        any_file_processed = False
        for file_info in files_to_process_info:
            # Check again if individual file exists before processing, in case one was created late but others failed the wait_for_files
            if os.path.exists(file_info["path"]):
                 process_and_embed_data(file_info["path"], file_info["collection"], file_info["source_name"])
                 any_file_processed = True # Mark that at least one processing attempt was made
            else:
                print(f"File {file_info['path']} was expected but not found at processing time. Skipping.")
        
        if any_file_processed:
            print("\n--- All embedding tasks attempted ---")
        else:
            print("\n--- No files were found to process for embedding ---")

    else: # This else block might be redundant if wait_for_files exits on failure
        print("Exiting due to some expected data files not being found.")
