from langchain.chains import RetrievalQA
# from langchain.llms import HuggingFaceEndpoint # No longer using HuggingFaceEndpoint directly
from langchain_openai import ChatOpenAI # Import ChatOpenAI
from langchain_qdrant import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings # Updated import
import os
from qdrant_client import QdrantClient

def build_chain():
    # Qdrant client should be initialized without embeddings if they are already stored
    # or ensure the client is configured correctly for how embeddings are handled.
    # For RetrievalQA, embeddings are typically part of the retriever setup.
    # The HuggingFaceEmbeddings here are for the retriever to understand how to process queries if needed,
    # not necessarily for re-embedding stored documents.
    embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
    
    # Initialize Qdrant client for connecting to the vector store
    qdrant_host = os.getenv("QDRANT_URL", "http://qdrant:6333").replace("http://", "").split(':')[0]
    qdrant_port = int(os.getenv("QDRANT_URL", "http://qdrant:6333").split(':')[-1])
    
    qdrant_direct_client = QdrantClient(host=qdrant_host, port=qdrant_port)
    
    # Use the existing Qdrant collection with the initialized client
    # Qdrant.construct_instance is not the standard way to get a vector store for retrieval.
    # Instead, we instantiate Qdrant from langchain_community.vectorstores with a client.
    vector_store = Qdrant(
        client=qdrant_direct_client,
        collection_name="nos_articles", 
        embeddings=embeddings
    )
    
    retriever = vector_store.as_retriever()

    llm = ChatOpenAI(
        openai_api_base=os.getenv("OPENAI_API_BASE", "http://llm_gateway:8000/v1"),
        openai_api_key=os.getenv("OPENAI_API_KEY", "dummy_key"), # LiteLLM may or may not need this based on its config
        model_name=os.getenv("LLM_MODEL_NAME", "custom_huggingface_model"),
        temperature=0.7,
        # max_tokens=512 # Optional: if you want to limit response length
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    return qa_chain
