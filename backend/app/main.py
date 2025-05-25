# backend/app/main.py

import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# ─── Load .env ───────────────────────────────────────────────────────
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# ─── Read env vars ────────────────────────────────────────────────────
AZURE_OPENAI_BASE        = os.getenv("AZURE_OPENAI_BASE")
AZURE_OPENAI_KEY         = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_CHAT_DEPLOY = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_OPENAI_EMBED_DEPLOY= os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")

SEARCH_ENDPOINT          = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY               = os.getenv("SEARCH_KEY")
SEARCH_INDEX             = os.getenv("SEARCH_INDEX_NAME")

# sanity‐check
missing = [
    n for n,v in [
        ("AZURE_OPENAI_BASE",AZURE_OPENAI_BASE),
        ("AZURE_OPENAI_KEY",AZURE_OPENAI_KEY),
        ("AZURE_OPENAI_CHAT_DEPLOY",AZURE_OPENAI_CHAT_DEPLOY),
        ("AZURE_OPENAI_EMBED_DEPLOY",AZURE_OPENAI_EMBED_DEPLOY),
        ("SEARCH_ENDPOINT",SEARCH_ENDPOINT),
        ("SEARCH_KEY",SEARCH_KEY),
        ("SEARCH_INDEX_NAME",SEARCH_INDEX),
    ] if not v
]
if missing:
    raise RuntimeError("Missing env vars: " + ", ".join(missing))

# ─── FastAPI + CORS ────────────────────────────────────────────────────
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ─── Clients ───────────────────────────────────────────────────────────
openai_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_BASE,
    api_key=AZURE_OPENAI_KEY,
    api_version="2025-01-01-preview",
)
search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=SEARCH_INDEX,
    credential=AzureKeyCredential(SEARCH_KEY),
)

# ─── Models ────────────────────────────────────────────────────────────
class Chapter(BaseModel):
    id:      int
    title:   str
    text:    str
    images:  List[str] = []

class ChatMessage(BaseModel):
    role:    str
    content: str

class ChatPayload(BaseModel):
    messages: List[ChatMessage]

# ─── Health ────────────────────────────────────────────────────────────
@app.get("/")
async def health():
    return {"status": "ok"}

# ─── TOC ────────────────────────────────────────────────────────────────
@app.get("/toc", response_model=List[Chapter])
async def get_toc():
    try:
        docs = search_client.search(
            search_text="*",
            top=20,
            query_type="simple"
        )
        chapters = []
        for idx, doc in enumerate(docs):
            # Use the metadata_storage_name or whatever your index uses for filename
            title = doc.get("metadata_storage_name", "")
            chapters.append(
                Chapter(
                    id=idx,
                    title=title or f"Chapter {idx+1}",
                    text=doc.get("content", ""),
                    images=doc.get("images", []),
                )
            )
        return chapters

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch TOC: {type(e).__name__}: {e}")

@app.post("/chat")
async def chat(payload: ChatPayload):
    try:
        ds = {
            "type": "azure_search",
            "parameters": {
                "endpoint": SEARCH_ENDPOINT,
                "index_name": SEARCH_INDEX,
                "query_type": "semantic",
                "semantic_configuration": "default",
                "authentication": {
                    "type": "api_key",
                    "key": SEARCH_KEY
                }
            }
        }

        resp = openai_client.chat.completions.create(
            model=AZURE_OPENAI_CHAT_DEPLOY,
            messages=[m.dict() for m in payload.messages],
            temperature=0.0,
            max_tokens=512,
            extra_body={"data_sources": [ds]},
        )
        return {"reply": resp.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")



