import os
import uuid
import json
import psycopg2
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from dotenv import load_dotenv
from api.models import QueryRequest, QueryResponse, SourceModel
from retrieval.retriever import retrieve
from retrieval.reranker import rerank
from retrieval.generator import generate_answer

load_dotenv()

router = APIRouter()

COST_PER_TOKEN = 0.000004
DAILY_QUERY_LIMIT = 50
MONTHLY_QUERY_LIMIT = 200000


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def setup_usage_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id UUID PRIMARY KEY,
            company_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT,
            tokens_used INTEGER,
            cost_usd FLOAT,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def check_daily_limit(company_id: str, user_id: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM query_logs
        WHERE company_id = %s
        AND user_id = %s
        AND timestamp >= NOW() - INTERVAL '24 hours'
    """, (company_id, user_id))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def check_monthly_limit(company_id: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM query_logs
        WHERE company_id = %s
        AND timestamp >= NOW() - INTERVAL '30 days'
    """, (company_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def log_query(
    company_id: str,
    user_id: str,
    question: str,
    answer: str,
    tokens_used: int
):
    conn = get_connection()
    cur = conn.cursor()
    query_id = str(uuid.uuid4())
    cost = tokens_used * COST_PER_TOKEN

    cur.execute("""
        INSERT INTO query_logs
        (id, company_id, user_id, question, answer, tokens_used, cost_usd)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (query_id, company_id, user_id, question, answer, tokens_used, cost))

    conn.commit()
    cur.close()
    conn.close()
    return query_id


@router.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):

    setup_usage_table()

    daily_count = check_daily_limit(request.company_id, request.user_id)
    if daily_count >= DAILY_QUERY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit of {DAILY_QUERY_LIMIT} queries reached. "
                   f"Resets in 24 hours."
        )

    monthly_count = check_monthly_limit(request.company_id)
    if monthly_count >= MONTHLY_QUERY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly limit of {MONTHLY_QUERY_LIMIT} queries reached. "
                   f"Please upgrade your plan."
        )

    try:
        results = retrieve(request.question, top_k=request.top_k)
        reranked = rerank(request.question, results)
        response = generate_answer(request.question, reranked)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    tokens_used = (
        response["input_tokens"] + response["output_tokens"]
    )

    query_id = log_query(
        company_id=request.company_id,
        user_id=request.user_id,
        question=request.question,
        answer=response["answer"],
        tokens_used=tokens_used
    )

    sources = []
    for s in response["sources"]:
        sources.append(SourceModel(
            filename=s.get("filename", "unknown"),
            page=int(s.get("page", 0)),
            score=float(s.get("rerank_score", 0))
        ))

    return QueryResponse(
        answer=response["answer"],
        sources=sources,
        tokens_used=tokens_used,
        query_id=query_id
    )