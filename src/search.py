"""
Semantic Search Engine
Main search functionality combining all components
"""

import numpy as np
from typing import List, Dict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SemanticSearch:
    """End-to-end semantic search engine"""
    
    def __init__(self, faiss_index=None, embedder=None, doc_mapping=None):
        """
        Initialize search engine
        
        Args:
            faiss_index: Built FAISS index or builder instance
            embedder: Embedding generator instance
            doc_mapping: Document ID to metadata mapping
        """
        self.faiss_index = faiss_index
        self.embedder = embedder
        self.doc_mapping = doc_mapping or {}
        
    def search(self, query: str, top_k: int = 10, 
               threshold: float = 0.0) -> List[Dict]:
        """
        Perform semantic search
        
        Args:
            query: Search query string
            top_k: Number of results to return
            threshold: Minimum similarity score threshold
            
        Returns:
            List of search result dictionaries
        """
        logger.info(f"Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.embedder.generate_embeddings(query, show_progress=False)
        
        # Search in FAISS index
        distances, indices = self.faiss_index.search(query_embedding, top_k=top_k * 2)
        
        # Format results
        results = []
        for i in range(len(indices[0])):
            doc_id = int(indices[0][i])
            
            # Skip invalid IDs
            if doc_id < 0 or doc_id >= len(self.doc_mapping):
                continue
            
            score = float(distances[0][i])
            
            # Apply threshold filter
            if score < threshold:
                continue
            
            # Get document metadata
            doc_info = self.doc_mapping.get(doc_id, {})
            
            result = {
                'rank': len(results) + 1,
                'document_id': doc_id,
                'text': doc_info.get('text', ''),
                'title': doc_info.get('title', ''),
                'similarity_score': score,
                'metadata': doc_info.get('metadata', {})
            }
            
            results.append(result)
            
            # Stop when we have enough results
            if len(results) >= top_k:
                break
        
        logger.info(f"Found {len(results)} results above threshold {threshold}")
        return results
    
    def batch_search(self, queries: List[str], top_k: int = 10,
                    threshold: float = 0.0) -> Dict[str, List[Dict]]:
        """
        Search multiple queries at once
        
        Args:
            queries: List of query strings
            top_k: Results per query
            threshold: Similarity threshold
            
        Returns:
            Dictionary mapping queries to their results
        """
        results_dict = {}
        
        for query in queries:
            results = self.search(query, top_k=top_k, threshold=threshold)
            results_dict[query] = results
        
        return results_dict


def format_search_results(distances: np.ndarray, indices: np.ndarray,
                         doc_mapping: Dict, top_k: int = 10) -> List[Dict]:
    """
    Format raw search results into readable format
    
    Args:
        distances: Distance/similarity scores from FAISS
        indices: Document indices from FAISS
        doc_mapping: Document metadata mapping
        top_k: Maximum number of results
        
    Returns:
        Formatted list of result dictionaries
    """
    results = []
    
    for i in range(len(indices[0])):
        doc_id = int(indices[0][i])
        
        if doc_id < 0:
            continue
        
        score = float(distances[0][i])
        doc_info = doc_mapping.get(doc_id, {})
        
        result = {
            'rank': len(results) + 1,
            'document_id': doc_id,
            'text': doc_info.get('text', ''),
            'title': doc_info.get('title', ''),
            'similarity_score': score,
            'metadata': doc_info.get('metadata', {})
        }
        
        results.append(result)
        
        if len(results) >= top_k:
            break
    
    return results
