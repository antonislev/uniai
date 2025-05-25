# backend/Dockerfile

# ─── 1) Base image ───────────────────────────────────────────────
FROM python:3.10-slim

# ─── 2) Set working directory ────────────────────────────────────
WORKDIR /app

# ─── 3) Copy your .env so load_dotenv() can read it at runtime ──
COPY .env ./

# ─── 4) Install Python dependencies ─────────────────────────────
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ─── 5) Copy your application code ───────────────────────────────
COPY ./app ./app

# ─── 6) Expose port & run Uvicorn ───────────────────────────────
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

