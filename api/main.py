"""
FastAPI application for Semantic Search Engine
"""
import time
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from utils.logger import setup_logger
from utils.config import API_HOST, API_PORT, API_DEBUG, BERT_MODEL_NAME
from search_engine.semantic_search import SemanticSearchEngine
from .schemas import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    BatchSearchRequest,
    BatchSearchResponse,
    HealthCheck,
    StatisticsResponse
)

logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Semantic Search Engine API",
    description="RESTful API for semantic search using BERT and FAISS",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global search engine instance
search_engine: SemanticSearchEngine = None


@app.on_event("startup")
async def startup_event():
    """Initialize search engine on startup."""
    global search_engine
    
    logger.info("Starting Semantic Search Engine API...")
    
    try:
        search_engine = SemanticSearchEngine()
        search_engine.initialize()
        
        logger.info("Search engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize search engine: {e}")
        raise


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Semantic Search Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    stats = search_engine.get_statistics()
    
    return HealthCheck(
        status="healthy",
        model_name=stats.get('model_name', 'unknown'),
        n_documents=stats.get('n_documents', 0),
        index_type=stats.get('index_type', 'unknown')
    )


@app.get("/stats", response_model=StatisticsResponse, tags=["Statistics"])
async def get_statistics():
    """Get search engine statistics."""
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    stats = search_engine.get_statistics()
    
    return StatisticsResponse(
        total_documents=stats.get('n_documents', 0),
        embedding_dimension=stats.get('embedding_dimension', 0),
        model_name=stats.get('model_name', 'unknown'),
        index_type=stats.get('index_type', 'unknown'),
        device="cuda" if "cuda" in str(stats.get('device', 'cpu')) else "cpu"
    )


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search(request: SearchRequest):
    """
    Search for documents similar to the query.
    
    - **query**: Search query text
    - **top_k**: Number of results to return (default: 10)
    - **threshold**: Minimum similarity score (default: 0.5)
    """
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    start_time = time.time()
    
    try:
        # Perform search
        results = search_engine.search(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Convert to Pydantic models
        search_results = [
            SearchResult(
                rank=r['rank'],
                document_id=r['document_id'],
                text=r['text'],
                title=r.get('title'),
                similarity_score=r['similarity_score'],
                metadata=r.get('metadata', {})
            )
            for r in results
        ]
        
        return SearchResponse(
            query=request.query,
            top_results=search_results,
            n_results=len(search_results),
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/search/batch", response_model=BatchSearchResponse, tags=["Search"])
async def batch_search(request: BatchSearchRequest):
    """
    Search for multiple queries at once.
    
    - **queries**: List of search queries
    - **top_k**: Number of results per query (default: 10)
    """
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    start_time = time.time()
    
    try:
        # Perform batch search
        all_results = search_engine.search_batch(
            queries=request.queries,
            top_k=request.top_k
        )
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Convert to Pydantic models
        batch_results = []
        for results in all_results:
            search_results = [
                SearchResult(
                    rank=r['rank'],
                    document_id=r['document_id'],
                    text=r['text'],
                    title=r.get('title'),
                    similarity_score=r['similarity_score'],
                    metadata=r.get('metadata', {})
                )
                for r in results
            ]
            batch_results.append(search_results)
        
        return BatchSearchResponse(
            results=batch_results,
            n_queries=len(request.queries),
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Batch search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch search failed: {str(e)}")


def run_server(host: str = None, port: int = None, reload: bool = False):
    """
    Run the FastAPI server.
    
    Args:
        host: Host address
        port: Port number
        reload: Enable auto-reload for development
    """
    host = host or API_HOST
    port = port or API_PORT
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    run_server(reload=API_DEBUG)
