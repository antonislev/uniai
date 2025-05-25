import os, openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from langchain_community.vectorstores import FAISS

class Query(BaseModel):
    question: str

# → Configure OpenAI for Azure
openai.api_type    = "azure"
openai.api_key     = os.getenv("AZURE_OPENAI_KEY")
openai.api_base    = os.getenv("AZURE_OPENAI_BASE")
openai.api_version = "2023-06-01-preview"

chat_dep = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
if not chat_dep:
    raise RuntimeError("Set AZURE_OPENAI_CHAT_DEPLOYMENT")

# Load FAISS index
idx_dir = Path(__file__).parent / "faiss_index"
if not idx_dir.exists():
    raise RuntimeError("Run prepare_index.py first!")
vs = FAISS.load_local(str(idx_dir), None, allow_dangerous_deserialization=True)
retriever = vs.as_retriever(search_kwargs={"k": 5})

app = FastAPI()

@app.post("/api/ask")
def ask(q: Query):
    try:
        docs = retriever.get_relevant_documents(q.question)
        context = "\n\n".join(d.page_content for d in docs)

        # → Use the new v1 chat interface
        resp = openai.ChatCompletion.create(
            model=chat_dep,       # your chat deployment name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {q.question}"}
            ],
            temperature=0
        )
        return {"answer": resp.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



