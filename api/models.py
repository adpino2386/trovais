from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class QueryRequest(BaseModel):
    question: str
    company_id: Optional[str] = "default"
    user_id: Optional[str] = "anonymous"
    top_k: Optional[int] = 5


class SourceModel(BaseModel):
    filename: str
    page: int
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceModel]
    tokens_used: int
    query_id: Optional[str] = None


class IngestRequest(BaseModel):
    filepath: str
    company_id: Optional[str] = "default"


class IngestResponse(BaseModel):
    success: bool
    filename: str
    chunks_ingested: int
    message: str


class UsageLog(BaseModel):
    company_id: str
    user_id: str
    question: str
    tokens_used: int
    timestamp: datetime
    cost_usd: float