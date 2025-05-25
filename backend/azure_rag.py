import os, json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from azure.identity import DefaultAzureCredential, AzureAuthorityHosts
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import AzureOpenAI

# ────────────────────────────────────────────────────
# 1) ENV VARS & CONSTANTS
# ────────────────────────────────────────────────────
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")         # e.g. https://smartrepagent.openai.azure.com
emb_dep  = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT") # e.g. embed-ada
chat_dep = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")  # e.g. chat-gpt35
api_ver  = "2023-06-01-preview"

for v in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_EMBED_DEPLOYMENT", "AZURE_OPENAI_CHAT_DEPLOYMENT"):
    if not os.getenv(v):
        raise RuntimeError(f"Missing environment variable: {v}")

# ────────────────────────────────────────────────────
# 2) SET UP AZURE AD AUTHENTICATION
# ────────────────────────────────────────────────────
# This will use Managed Identity (if deployed) or your local Azure login.
credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_PUBLIC_CLOUD)
token_provider = lambda *scopes: credential.get_token(*scopes).token

# ────────────────────────────────────────────────────
# 3) BUILD OR LOAD FAISS INDEX (EMBEDDINGS)
# ────────────────────────────────────────────────────
INDEX_DIR = Path(__file__).parent / "faiss_index"
DATA_JSON = Path(__file__).parent.parent / "frontend" / "public" / "docs" / "data.json"

# Create an OpenAI client that uses AD tokens for embeddings
openai_client = OpenAI(
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider,
    api_version=api_ver
)

if not INDEX_DIR.exists():
    # Load your manual (Greek) from JSON
    raw = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    chapters = raw if isinstance(raw, list) else [raw]
    texts = [c["text"] for c in chapters]

    # Request embeddings in batch
    resp = openai_client.embeddings.create(
        deployment_id=emb_dep,
        input=texts
    )
    embeddings = [item["embedding"] for item in resp["data"]]

    # Build & persist FAISS index
    vs = FAISS.from_embeddings(embeddings, texts)
    vs.save_local(str(INDEX_DIR))
    print("✅ Built FAISS index at", INDEX_DIR)

# Load the FAISS index and attach the same embeddings extractor for similarity
vs = FAISS.load_local(
    str(INDEX_DIR),
    embedding= lambda texts: openai_client.embeddings.create(deployment_id=emb_dep, input=texts).data,  # OR use a proper Embeddings object
    allow_dangerous_deserialization=True
)
retriever = vs.as_retriever(search_kwargs={"k": 5})

# ────────────────────────────────────────────────────
# 4) CONFIGURE AZURE CHAT LLM (RAG)
# ────────────────────────────────────────────────────
llm = AzureOpenAI(
    azure_ad_token_provider=token_provider,
    azure_endpoint=endpoint,
    deployment_name=chat_dep,
    api_version=api_ver,
    temperature=0
)

qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# ────────────────────────────────────────────────────
# 5) FASTAPI APP
# ────────────────────────────────────────────────────
app = FastAPI(title="BMW X1 Manual QA")

class Query(BaseModel):
    question: str

@app.post("/api/ask")
def ask(q: Query):
    try:
        answer = qa.run(q.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


