import os
import psycopg2
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from api.routes import query, ingest

load_dotenv()

app = FastAPI(
    title="Trovais API",
    description="AI-powered knowledge retrieval for enterprise documents",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(ingest.router, prefix="/api/v1", tags=["Ingest"])


# ── Keep Supabase alive (pings every 6 days) ──────────────────────────────────
def ping_database():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM documents")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        print(f"Keep-alive ping successful — {count} chunks in database")
    except Exception as e:
        print(f"Keep-alive ping failed: {e}")


scheduler = BackgroundScheduler()
scheduler.add_job(ping_database, "interval", days=6)
scheduler.start()


@app.get("/")
def root():
    return {
        "product": "Trovais",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
