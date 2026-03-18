"""
Core semantic search functionality
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from utils.logger import setup_logger
from utils.config import (
    TOP_K_RESULTS,
    SIMILARITY_THRESHOLD,
    BERT_MODEL_NAME,
    FAISS_INDEX_FILE,
    METADATA_FILE,
    EMBEDDINGS_CACHE_FILE
)
from embeddings.embedding_generator import EmbeddingGenerator
from vector_database.faiss_index import FAISSIndex
from vector_database.index_utils import (
    load_index_metadata,
    format_search_results,
    get_index_statistics
)

logger = setup_logger(__name__)


class SemanticSearchEngine:
    """
    Main semantic search engine combining embeddings and FAISS.
    """
    
    def __init__(
        self,
        model_name: str = None,
        faiss_index_file: Path = None,
        metadata_file: Path = None,
        embeddings_file: Path = None
    ):
        """
        Initialize the semantic search engine.
        
        Args:
            model_name: Sentence-BERT model to use
            faiss_index_file: Path to FAISS index file
            metadata_file: Path to document metadata file
            embeddings_file: Path to cached embeddings file
        """
        self.model_name = model_name or BERT_MODEL_NAME
        self.faiss_index_file = faiss_index_file or FAISS_INDEX_FILE
        self.metadata_file = metadata_file or METADATA_FILE
        self.embeddings_file = embeddings_file or EMBEDDINGS_CACHE_FILE
        
        # Initialize components
        self.embedding_generator = None
        self.faiss_index = None
        self.document_metadata = None
        
        logger.info(f"SemanticSearchEngine initialized with model: {self.model_name}")
    
    def initialize(self) -> None:
        """
        Initialize all components (model, index, metadata).
        """
        logger.info("Initializing search engine components...")
        
        # Load embedding generator
        self.embedding_generator = EmbeddingGenerator(model_name=self.model_name)
        
        # Load FAISS index
        self.faiss_index = FAISSIndex(
            embedding_dim=self.embedding_generator.get_embedding_dimension()
        )
        self.faiss_index.load(self.faiss_index_file)
        
        # Load document metadata
        self.document_metadata = load_index_metadata(self.metadata_file)
        
        logger.info(f"Search engine initialized with {len(self.document_metadata)} documents")
    
    def search(
        self,
        query: str,
        top_k: int = None,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            threshold: Minimum similarity score threshold
            
        Returns:
            List of search result dictionaries
        """
        top_k = top_k or TOP_K_RESULTS
        threshold = threshold or SIMILARITY_THRESHOLD
        
        if self.embedding_generator is None or self.faiss_index is None:
            self.initialize()
        
        logger.info(f"Searching for query: '{query[:50]}...'")
        
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embeddings(
            query,
            show_progress=False
        )
        
        # Search in FAISS index
        distances, indices = self.faiss_index.search(query_embedding, top_k=top_k * 2)
        
        # Format results
        results = format_search_results(
            distances,
            indices,
            self.document_metadata,
            top_k=top_k
        )
        
        # Apply threshold filter
        filtered_results = [
            r for r in results
            if r['similarity_score'] >= threshold
        ]
        
        # Sort by similarity score (descending)
        filtered_results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Update ranks
        for i, result in enumerate(filtered_results):
            result['rank'] = i + 1
        
        logger.info(f"Found {len(filtered_results)} results above threshold")
        
        return filtered_results
    
    def search_batch(
        self,
        queries: List[str],
        top_k: int = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Search for multiple queries at once.
        
        Args:
            queries: List of query texts
            top_k: Number of results per query
            
        Returns:
            List of result lists (one per query)
        """
        top_k = top_k or TOP_K_RESULTS
        
        if self.embedding_generator is None or self.faiss_index is None:
            self.initialize()
        
        logger.info(f"Batch searching {len(queries)} queries")
        
        # Generate embeddings for all queries
        query_embeddings = self.embedding_generator.generate_embeddings(
            queries,
            show_progress=False
        )
        
        # Search for all queries
        distances, indices = self.faiss_index.search_batch(query_embeddings, top_k=top_k)
        
        # Format results for each query
        all_results = []
        for i in range(len(queries)):
            results = format_search_results(
                distances[i:i+1],
                indices[i:i+1],
                self.document_metadata,
                top_k=top_k
            )
            all_results.append(results)
        
        return all_results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get search engine statistics.
        
        Returns:
            Dictionary containing statistics
        """
        stats = {
            'model_name': self.model_name,
            'n_documents': len(self.document_metadata) if self.document_metadata else 0,
            'embedding_dimension': self.embedding_generator.get_embedding_dimension() 
                                 if self.embedding_generator else 0
        }
        
        # Add FAISS index stats
        try:
            index_stats = get_index_statistics(self.faiss_index_file)
            stats.update(index_stats)
        except Exception as e:
            logger.warning(f"Could not get index stats: {e}")
        
        return stats


def create_search_engine(
    model_name: str = None,
    initialize: bool = True
) -> SemanticSearchEngine:
    """
    Convenience function to create a search engine.
    
    Args:
        model_name: Optional model name override
        initialize: Whether to initialize components immediately
        
    Returns:
        Initialized SemanticSearchEngine instance
    """
    engine = SemanticSearchEngine(model_name=model_name)
    
    if initialize:
        engine.initialize()
    
    return engine


def quick_search(
    query: str,
    top_k: int = 5,
    model_name: str = None
) -> List[Dict[str, Any]]:
    """
    Quick search function that creates engine and searches in one call.
    
    Args:
        query: Search query
        top_k: Number of results
        model_name: Model to use
        
    Returns:
        Search results
    """
    engine = create_search_engine(model_name=model_name)
    return engine.search(query, top_k=top_k)
