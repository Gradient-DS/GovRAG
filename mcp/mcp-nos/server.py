from typing import List
from contextlib import asynccontextmanager

from qdrant_client import QdrantClient
from mcp.server.fastmcp import FastMCP, Context
from starlette.concurrency import run_in_threadpool

from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")

@asynccontextmanager
async def lifespan(server):
    client = QdrantClient(host="qdrant", port=6333)
    try:
        yield {"qdrant": client}
    finally:
        client.close()

mcp = FastMCP(
    name="NOSNews",
    lifespan=lifespan,
    dependencies=["qdrant-client", "langchain-huggingface"]
)

@mcp.tool(
    "nos_articles/text_search",
    description="Embed your natural-language query and retrieve the top-K matching news articles."
)
async def text_search(
    query: str,
    ctx: Context,
    top_k: int = 10,
    min_score: float = 0.0
):
    vector = await run_in_threadpool(embeddings.embed_query, query)

    qdrant: QdrantClient = ctx.request_context.lifespan_context["qdrant"]
    hits = qdrant.search(
        collection_name="nos_articles",
        query_vector=vector,
        limit=top_k,
        with_payload=True,
        score_threshold=(min_score or None)
    )

    return [
        {"id": h.id, "score": h.score, "payload": h.payload}
        for h in hits
    ]

app = mcp

if __name__ == "__main__":
    mcp.run()
