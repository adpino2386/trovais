import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
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