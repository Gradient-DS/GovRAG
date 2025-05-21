from fastapi import FastAPI, Request
from chains import build_chain

app = FastAPI()
chain = build_chain()

@app.post("/")
async def rag_endpoint(request: Request):
    data = await request.json()
    question = data.get("message") or data.get("prompt")
    result = chain.invoke({"input": question})
    return {"content": result}