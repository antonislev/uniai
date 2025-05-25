import os, json, openai
from pathlib import Path
from langchain_community.vectorstores import FAISS

def main():
    key   = os.getenv("AZURE_OPENAI_KEY")
    base  = os.getenv("AZURE_OPENAI_BASE")
    embed = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")
    if not (key and base and embed):
        raise RuntimeError("Set AZURE_OPENAI_KEY, AZURE_OPENAI_BASE & AZURE_OPENAI_EMBED_DEPLOYMENT")

    # → Configure OpenAI for Azure
    openai.api_type    = "azure"
    openai.api_key     = key
    openai.api_base    = base
    openai.api_version = "2023-06-01-preview"

    # Load your manual export
    docs_path = Path(__file__).parent.parent / "frontend" / "public" / "docs" / "data.json"
    chapters  = json.loads(docs_path.read_text(encoding="utf-8"))
    texts     = [c["text"] for c in chapters]

    # → Use the new v1 embeddings interface
    resp = openai.embeddings.create(
        model=embed,    # your embed deployment name
        input=texts
    )
    embeddings = [d["embedding"] for d in resp["data"]]

    # Build & save FAISS
    vs = FAISS.from_embeddings(embeddings, texts)
    out = Path(__file__).parent / "faiss_index"
    vs.save_local(str(out))
    print("✅ FAISS index built to", out)

if __name__ == "__main__":
    main()

