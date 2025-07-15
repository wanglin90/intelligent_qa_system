from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentUpload(BaseModel):
    filename: str
    content_type: str
    size: int


class DocumentInfo(BaseModel):
    id: str
    filename: str
    upload_time: datetime
    chunks_count: int
    status: str
    metadata: Dict[str, Any] = {}


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    max_results: Optional[int] = 5


class SourceInfo(BaseModel):
    source: str
    chunk_id: str
    score: float
    content_preview: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    confidence: float
    retrieved_count: int
    processing_time: float
    session_id: Optional[str] = None


class HealthCheck(BaseModel):
    status: str
    message: str
    timestamp: datetime
    version: str = "1.0.0"