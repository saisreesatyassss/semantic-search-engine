"""
FAISS Index Builder and Manager
Create and manage vector search indices
"""

import faiss
import numpy as np
from typing import Union, Tuple
from pathlib import Path
import logging
import pickle

logger = logging.getLogger(__name__)


class FAISSIndexBuilder:
    """Build and manage FAISS indices"""
    
    def __init__(self, embedding_dim: int = 384, 
                 index_type: str = "IndexFlatL2",
                 metric: str = "cosine"):
        """
        Initialize FAISS index builder
        
        Args:
            embedding_dim: Dimension of embeddings
            index_type: Type of FAISS index
            metric: Distance metric ('cosine' or 'L2')
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.metric = metric
        
        logger.info(f"Initializing FAISS index: {index_type}, dim={embedding_dim}")
        self.index = self._create_index()
    
    def _create_index(self):
        """Create FAISS index based on type"""
        if self.index_type == "IndexFlatL2":
            return faiss.IndexFlatL2(self.embedding_dim)
        elif self.index_type == "IndexFlatIP":
            return faiss.IndexFlatIP(self.embedding_dim)
        else:
            raise ValueError(f"Unknown index type: {self.index_type}")
    
    def add_embeddings(self, embeddings: np.ndarray):
        """
        Add embeddings to index
        
        Args:
            embeddings: Numpy array of embeddings (n_documents, embedding_dim)
        """
        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
        
        # Normalize for cosine similarity
        if self.metric == 'cosine':
            faiss.normalize_L2(embeddings)
            logger.info("Normalized embeddings for cosine similarity")
        
        n_added = embeddings.shape[0]
        self.index.add(embeddings)
        
        logger.info(f"Added {n_added} embeddings to index. Total: {self.index.ntotal}")
    
    def build_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Build complete index from embeddings
        
        Args:
            embeddings: Array of document embeddings
            
        Returns:
            Built FAISS index
        """
        logger.info(f"Building index with {len(embeddings)} embeddings...")
        self.add_embeddings(embeddings)
        logger.info("Index built successfully!")
        return self.index
    
    def save_index(self, output_path: Union[str, Path]):
        """Save FAISS index to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(self.index, str(output_path))
        logger.info(f"Index saved to {output_path}")
    
    def load_index(self, input_path: Union[str, Path]) -> faiss.Index:
        """Load FAISS index from file"""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Index file not found: {input_path}")
        
        self.index = faiss.read_index(str(input_path))
        logger.info(f"Index loaded from {input_path}. Total vectors: {self.index.ntotal}")
        return self.index
    
    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search in index
        
        Args:
            query_embedding: Query vector (1, embedding_dim)
            top_k: Number of results to return
            
        Returns:
            Tuple of (distances, indices)
        """
        query_embedding = np.ascontiguousarray(query_embedding, dtype=np.float32)
        
        # Normalize query for cosine similarity
        if self.metric == 'cosine':
            faiss.normalize_L2(query_embedding)
        
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Convert L2 distances to similarity scores for cosine metric
        if self.metric == 'cosine':
            # For normalized vectors, inner product = cosine similarity
            pass
        elif self.metric == 'L2':
            # Convert L2 distance to similarity (smaller distance = higher similarity)
            distances = 1 / (1 + distances)
        
        return distances, indices
    
    def get_index_stats(self) -> dict:
        """Get index statistics"""
        return {
            'ntotal': self.index.ntotal,
            'dimension': self.index.d,
            'index_type': self.index_type,
            'metric': self.metric,
            'is_trained': self.index.is_trained
        }


def build_faiss_index(embeddings: np.ndarray, **kwargs) -> faiss.Index:
    """Convenience function to build FAISS index"""
    builder = FAISSIndexBuilder(**kwargs)
    return builder.build_index(embeddings)


def create_document_mapping(documents: list, output_path: Union[str, Path] = None):
    """
    Create mapping between document IDs and metadata
    
    Args:
        documents: List of document dictionaries
        output_path: Optional path to save mapping
        
    Returns:
        Dictionary mapping doc_id to metadata
    """
    doc_mapping = {}
    for idx, doc in enumerate(documents):
        doc_mapping[idx] = {
            'id': idx,
            'text': doc.get('text', ''),
            'title': doc.get('title', ''),
            'metadata': doc.get('metadata', {})
        }
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            pickle.dump(doc_mapping, f)
        logger.info(f"Document mapping saved to {output_path}")
    
    return doc_mapping


def load_document_mapping(input_path: Union[str, Path]) -> dict:
    """Load document mapping from file"""
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Mapping file not found: {input_path}")
    
    with open(input_path, 'rb') as f:
        doc_mapping = pickle.load(f)
    
    logger.info(f"Loaded mapping for {len(doc_mapping)} documents")
    return doc_mapping
