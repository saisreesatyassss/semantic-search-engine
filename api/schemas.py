"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class SearchRequest(BaseModel):
    """
    Request schema for search endpoint.
    """
    query: str = Field(..., description="Search query text", min_length=1, max_length=1000)
    top_k: int = Field(default=10, description="Number of results to return", ge=1, le=100)
    threshold: float = Field(default=0.5, description="Minimum similarity score", ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "deep learning for medical imaging",
                "top_k": 10,
                "threshold": 0.5
            }
        }


class SearchResult(BaseModel):
    """
    Schema for a single search result.
    """
    rank: int = Field(..., description="Result rank")
    document_id: int = Field(..., description="Document ID")
    text: str = Field(..., description="Document text")
    title: Optional[str] = Field(None, description="Document title")
    similarity_score: float = Field(..., description="Similarity score")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class SearchResponse(BaseModel):
    """
    Response schema for search endpoint.
    """
    query: str = Field(..., description="Original query")
    top_results: List[SearchResult] = Field(..., description="List of search results")
    n_results: int = Field(..., description="Total number of results")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "deep learning for medical imaging",
                "top_results": [
                    {
                        "rank": 1,
                        "document_id": 123,
                        "text": "Deep learning applications in medical imaging...",
                        "title": "Medical Imaging with AI",
                        "similarity_score": 0.89,
                        "metadata": {}
                    }
                ],
                "n_results": 1,
                "processing_time_ms": 45.2
            }
        }


class BatchSearchRequest(BaseModel):
    """
    Request schema for batch search endpoint.
    """
    queries: List[str] = Field(..., description="List of search queries", min_length=1, max_length=100)
    top_k: int = Field(default=10, description="Number of results per query", ge=1, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "queries": [
                    "machine learning basics",
                    "neural networks architecture"
                ],
                "top_k": 5
            }
        }


class BatchSearchResponse(BaseModel):
    """
    Response schema for batch search endpoint.
    """
    results: List[List[SearchResult]] = Field(..., description="Results for each query")
    n_queries: int = Field(..., description="Number of queries processed")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")


class HealthCheck(BaseModel):
    """
    Health check response schema.
    """
    status: str = Field(..., description="Service status")
    model_name: str = Field(..., description="Loaded model name")
    n_documents: int = Field(..., description="Number of indexed documents")
    index_type: str = Field(..., description="FAISS index type")


class StatisticsResponse(BaseModel):
    """
    Statistics response schema.
    """
    total_documents: int = Field(..., description="Total number of documents")
    embedding_dimension: int = Field(..., description="Embedding vector dimension")
    model_name: str = Field(..., description="Model name")
    index_type: str = Field(..., description="Index type")
    device: str = Field(..., description="Device being used (CPU/GPU)")
