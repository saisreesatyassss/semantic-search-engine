"""
Ranking and scoring utilities for search results
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ResultRanker:
    """
    Advanced ranking utilities for search results.
    """
    
    def __init__(self, score_threshold: float = 0.5):
        """
        Initialize the result ranker.
        
        Args:
            score_threshold: Minimum similarity score threshold
        """
        self.score_threshold = score_threshold
        logger.info(f"ResultRanker initialized with threshold={score_threshold}")
    
    def rerank_by_similarity(
        self,
        results: List[Dict[str, Any]],
        query_embedding: np.ndarray,
        method: str = 'cosine'
    ) -> List[Dict[str, Any]]:
        """
        Rerank results using different similarity methods.
        
        Args:
            results: List of result dictionaries with embeddings
            query_embedding: Query embedding vector
            method: Similarity method ('cosine', 'euclidean')
            
        Returns:
            Reranked results
        """
        if not results:
            return results
        
        # Extract document embeddings if available
        if 'embedding' in results[0]:
            doc_embeddings = np.array([r['embedding'] for r in results])
            
            if method == 'cosine':
                similarities = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    doc_embeddings
                )[0]
            elif method == 'euclidean':
                # Convert Euclidean distance to similarity
                distances = np.linalg.norm(doc_embeddings - query_embedding, axis=1)
                similarities = 1 / (1 + distances)
            else:
                raise ValueError(f"Unknown similarity method: {method}")
            
            # Update scores
            for i, result in enumerate(results):
                result['similarity_score'] = float(similarities[i])
        
        # Sort by similarity (descending)
        ranked_results = sorted(
            results,
            key=lambda x: x['similarity_score'],
            reverse=True
        )
        
        # Update ranks
        for i, result in enumerate(ranked_results):
            result['rank'] = i + 1
        
        logger.info(f"Reranked {len(ranked_results)} results")
        
        return ranked_results
    
    def apply_diversity_penalty(
        self,
        results: List[Dict[str, Any]],
        diversity_factor: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Apply diversity penalty to reduce redundancy in results.
        
        Args:
            results: Ranked results
            diversity_factor: Penalty factor for similar results
            
        Returns:
            Diversified results
        """
        if len(results) <= 1:
            return results
        
        diversified = [results[0]]  # Keep top result unchanged
        
        for i in range(1, len(results)):
            current = results[i]
            
            # Calculate max similarity to already selected results
            max_sim = 0
            for selected in diversified:
                sim = current['similarity_score'] * 0.5  # Simplified diversity measure
            
            # Apply penalty
            penalty = max_sim * diversity_factor
            current['adjusted_score'] = current['similarity_score'] - penalty
            
            diversified.append(current)
        
        # Re-sort by adjusted score
        diversified.sort(key=lambda x: x.get('adjusted_score', x['similarity_score']), reverse=True)
        
        # Update ranks
        for i, result in enumerate(diversified):
            result['rank'] = i + 1
        
        logger.info(f"Applied diversity penalty to {len(diversified)} results")
        
        return diversified
    
    def filter_by_threshold(
        self,
        results: List[Dict[str, Any]],
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Filter results below similarity threshold.
        
        Args:
            results: List of results
            threshold: Score threshold
            
        Returns:
            Filtered results
        """
        threshold = threshold or self.score_threshold
        
        filtered = [
            r for r in results
            if r['similarity_score'] >= threshold
        ]
        
        # Update ranks
        for i, result in enumerate(filtered):
            result['rank'] = i + 1
        
        logger.info(f"Filtered to {len(filtered)} results above threshold {threshold}")
        
        return filtered
    
    def normalize_scores(
        self,
        results: List[Dict[str, Any]],
        method: str = 'minmax'
    ) -> List[Dict[str, Any]]:
        """
        Normalize similarity scores to [0, 1] range.
        
        Args:
            results: Results to normalize
            method: Normalization method ('minmax', 'softmax')
            
        Returns:
            Results with normalized scores
        """
        if not results:
            return results
        
        scores = np.array([r['similarity_score'] for r in results])
        
        if method == 'minmax':
            min_score = scores.min()
            max_score = scores.max()
            
            if max_score - min_score > 0:
                normalized = (scores - min_score) / (max_score - min_score)
            else:
                normalized = scores
        elif method == 'softmax':
            # Apply softmax for probability distribution
            exp_scores = np.exp(scores - scores.max())
            normalized = exp_scores / exp_scores.sum()
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        # Update scores
        for i, result in enumerate(results):
            result['normalized_score'] = float(normalized[i])
        
        logger.info(f"Normalized {len(results)} scores using {method} method")
        
        return results


def calculate_recall_at_k(
    relevant_docs: set,
    retrieved_docs: list,
    k: int = 10
) -> float:
    """
    Calculate Recall@K metric.
    
    Args:
        relevant_docs: Set of relevant document IDs
        retrieved_docs: List of retrieved document IDs (ranked)
        k: Number of results to consider
        
    Returns:
        Recall@K score
    """
    if not relevant_docs:
        return 0.0
    
    top_k_docs = set(retrieved_docs[:k])
    relevant_retrieved = len(top_k_docs.intersection(relevant_docs))
    
    recall = relevant_retrieved / len(relevant_docs)
    
    logger.info(f"Recall@{k}: {recall:.4f}")
    
    return recall


def calculate_precision_at_k(
    relevant_docs: set,
    retrieved_docs: list,
    k: int = 10
) -> float:
    """
    Calculate Precision@K metric.
    
    Args:
        relevant_docs: Set of relevant document IDs
        retrieved_docs: List of retrieved document IDs (ranked)
        k: Number of results to consider
        
    Returns:
        Precision@K score
    """
    if k == 0:
        return 0.0
    
    top_k_docs = set(retrieved_docs[:k])
    relevant_retrieved = len(top_k_docs.intersection(relevant_docs))
    
    precision = relevant_retrieved / k
    
    logger.info(f"Precision@{k}: {precision:.4f}")
    
    return precision


def calculate_mean_reciprocal_rank(
    relevant_docs: set,
    retrieved_docs: list
) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR).
    
    Args:
        relevant_docs: Set of relevant document IDs
        retrieved_docs: List of retrieved document IDs (ranked)
        
    Returns:
        MRR score
    """
    for i, doc_id in enumerate(retrieved_docs):
        if doc_id in relevant_docs:
            mrr = 1.0 / (i + 1)
            logger.info(f"MRR: {mrr:.4f}")
            return mrr
    
    return 0.0


def evaluate_search_quality(
    query_results: List[Dict[str, Any]],
    ground_truth_relevant_ids: set
) -> Dict[str, float]:
    """
    Evaluate search quality with multiple metrics.
    
    Args:
        query_results: Search results from a query
        ground_truth_relevant_ids: Set of truly relevant document IDs
        
    Returns:
        Dictionary of evaluation metrics
    """
    retrieved_ids = [r['document_id'] for r in query_results]
    
    metrics = {
        'recall@5': calculate_recall_at_k(ground_truth_relevant_ids, retrieved_ids, k=5),
        'recall@10': calculate_recall_at_k(ground_truth_relevant_ids, retrieved_ids, k=10),
        'precision@5': calculate_precision_at_k(ground_truth_relevant_ids, retrieved_ids, k=5),
        'precision@10': calculate_precision_at_k(ground_truth_relevant_ids, retrieved_ids, k=10),
        'mrr': calculate_mean_reciprocal_rank(ground_truth_relevant_ids, retrieved_ids)
    }
    
    return metrics
