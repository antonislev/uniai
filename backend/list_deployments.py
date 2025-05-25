import os, requests

key  = os.getenv("AZURE_OPENAI_KEY")
# Remove any trailing slash here:
base = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
if not (key and base):
    raise RuntimeError("Set AZURE_OPENAI_KEY & AZURE_OPENAI_ENDPOINT")

url = f"{base}/openai/deployments?api-version=2023-06-01-preview"
resp = requests.get(url, headers={"api-key": key})
resp.raise_for_status()
print(resp.json())

