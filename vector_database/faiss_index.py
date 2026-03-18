"""
FAISS index creation and management for vector similarity search
"""
import numpy as np
import faiss
from pathlib import Path
from typing import Tuple, Optional
from utils.logger import setup_logger
from utils.config import (
    FAISS_INDEX_TYPE,
    FAISS_NPROBE,
    FAISS_METRIC,
    VECTOR_DB_DIR,
    DEVICE
)

logger = setup_logger(__name__)


class FAISSIndex:
    """
    Manages FAISS index for efficient similarity search.
    """
    
    def __init__(
        self,
        embedding_dim: int,
        index_type: str = None,
        metric: str = None
    ):
        """
        Initialize FAISS index manager.
        
        Args:
            embedding_dim: Dimension of embeddings
            index_type: Type of FAISS index to create
            metric: Similarity metric ('cosine' or 'L2')
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type or FAISS_INDEX_TYPE
        self.metric = metric or FAISS_METRIC
        self.index = None
        self.is_trained = False
        
        logger.info(f"FAISSIndex initialized with dim={embedding_dim}, "
                   f"type={self.index_type}, metric={self.metric}")
    
    def create_index(self) -> faiss.Index:
        """
        Create a new FAISS index based on configuration.
        
        Returns:
            Created FAISS index
        """
        logger.info(f"Creating {self.index_type} index")
        
        if self.metric == 'cosine':
            # For cosine similarity, we normalize vectors and use inner product
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            logger.info("Using IndexFlatIP for cosine similarity (normalized vectors)")
        elif self.metric == 'L2':
            # Euclidean distance
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            logger.info("Using IndexFlatL2 for Euclidean distance")
        else:
            raise ValueError(f"Unsupported metric: {self.metric}")
        
        self.is_trained = True  # Flat indexes don't need training
        
        return self.index
    
    def create_ivf_index(
        self,
        n_clusters: int = 100,
        nprobe: int = None
    ) -> faiss.Index:
        """
        Create an IVF (Inverted File) index for larger datasets.
        
        Args:
            n_clusters: Number of clusters for IVF
            nprobe: Number of clusters to search
            
        Returns:
            Created IVF index
        """
        nprobe = nprobe or FAISS_NPROBE
        
        logger.info(f"Creating IVF index with n_clusters={n_clusters}, nprobe={nprobe}")
        
        # Create quantizer
        quantizer = faiss.IndexFlatL2(self.embedding_dim)
        
        # Create IVF index
        self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, n_clusters, faiss.METRIC_L2)
        
        self.nprobe = nprobe
        self.is_trained = False  # IVF index needs training
        
        return self.index
    
    def train_index(self, embeddings: np.ndarray) -> None:
        """
        Train the index with sample embeddings.
        
        Args:
            embeddings: Training embeddings (n_samples, embedding_dim)
        """
        if not self.is_trained and hasattr(self.index, 'train'):
            logger.info(f"Training index with {len(embeddings)} samples")
            
            # Ensure contiguous array
            embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
            
            self.index.train(embeddings)
            self.is_trained = True
            
            logger.info("Index training completed")
    
    def add_embeddings(
        self,
        embeddings: np.ndarray,
        ids: Optional[np.ndarray] = None
    ) -> None:
        """
        Add embeddings to the index.
        
        Args:
            embeddings: Embeddings to add (n_embeddings, embedding_dim)
            ids: Optional IDs for the embeddings
        """
        if self.index is None:
            raise RuntimeError("Index not created. Call create_index() first.")
        
        # Ensure float32 and contiguous
        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
        
        # Normalize for cosine similarity
        if self.metric == 'cosine':
            faiss.normalize_L2(embeddings)
        
        logger.info(f"Adding {len(embeddings)} embeddings to index")
        
        if ids is not None:
            self.index.add_with_ids(embeddings, ids.astype(np.int64))
        else:
            self.index.add(embeddings)
        
        logger.info(f"Index now contains {self.index.ntotal} vectors")
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for similar vectors in the index.
        
        Args:
            query_embedding: Query vector (embedding_dim,) or (1, embedding_dim)
            top_k: Number of results to return
            
        Returns:
            Tuple of (distances, indices) arrays
        """
        if self.index is None:
            raise RuntimeError("Index not created")
        
        # Ensure 2D array
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        query_embedding = np.ascontiguousarray(query_embedding, dtype=np.float32)
        
        # Normalize for cosine similarity
        if self.metric == 'cosine':
            faiss.normalize_L2(query_embedding)
        
        # Set nprobe for IVF index
        if hasattr(self, 'nprobe') and hasattr(self.index, 'nprobe'):
            self.index.nprobe = self.nprobe
        
        # Perform search
        distances, indices = self.index.search(query_embedding, top_k)
        
        logger.debug(f"Search returned {len(indices[0])} results")
        
        return distances, indices
    
    def search_batch(
        self,
        query_embeddings: np.ndarray,
        top_k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for multiple queries at once.
        
        Args:
            query_embeddings: Query vectors (n_queries, embedding_dim)
            top_k: Number of results per query
            
        Returns:
            Tuple of (distances, indices) arrays
        """
        if self.index is None:
            raise RuntimeError("Index not created")
        
        query_embeddings = np.ascontiguousarray(query_embeddings, dtype=np.float32)
        
        # Normalize for cosine similarity
        if self.metric == 'cosine':
            faiss.normalize_L2(query_embeddings)
        
        # Set nprobe for IVF index
        if hasattr(self, 'nprobe') and hasattr(self.index, 'nprobe'):
            self.index.nprobe = self.nprobe
        
        # Perform batch search
        distances, indices = self.index.search(query_embeddings, top_k)
        
        logger.debug(f"Batch search for {len(query_embeddings)} queries")
        
        return distances, indices
    
    def save(self, filepath: Optional[Path] = None) -> Path:
        """
        Save the index to disk.
        
        Args:
            filepath: Output file path
            
        Returns:
            Path to saved file
        """
        if self.index is None:
            raise RuntimeError("No index to save")
        
        filepath = filepath or (Path(VECTOR_DB_DIR) / "faiss.index")
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(self.index, str(filepath))
        
        logger.info(f"Saved index to {filepath}")
        
        return filepath
    
    def load(self, filepath: Optional[Path] = None) -> faiss.Index:
        """
        Load index from disk.
        
        Args:
            filepath: File path to load from
            
        Returns:
            Loaded FAISS index
        """
        filepath = filepath or (Path(VECTOR_DB_DIR) / "faiss.index")
        
        if not filepath.exists():
            raise FileNotFoundError(f"Index file not found: {filepath}")
        
        self.index = faiss.read_index(str(filepath))
        
        logger.info(f"Loaded index from {filepath} ({self.index.ntotal} vectors)")
        
        self.is_trained = True
        
        return self.index
    
    def get_stats(self) -> dict:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        if self.index is None:
            return {}
        
        stats = {
            'ntotal': self.index.ntotal,
            'dimension': self.embedding_dim,
            'index_type': self.index_type,
            'metric': self.metric,
            'is_trained': self.is_trained
        }
        
        if hasattr(self, 'nprobe'):
            stats['nprobe'] = self.nprobe
        
        return stats


def build_faiss_index(
    embeddings: np.ndarray,
    index_type: str = None,
    metric: str = None,
    save_path: Optional[Path] = None
) -> FAISSIndex:
    """
    Convenience function to build and populate a FAISS index.
    
    Args:
        embeddings: Embeddings to index
        index_type: Type of index to create
        metric: Similarity metric
        save_path: Optional path to save index
        
    Returns:
        Created and populated FAISSIndex instance
    """
    embedding_dim = embeddings.shape[1]
    
    # Create index manager
    faiss_index = FAISSIndex(
        embedding_dim=embedding_dim,
        index_type=index_type,
        metric=metric
    )
    
    # Create appropriate index
    if len(embeddings) > 100000 and index_type == 'IndexIVFFlat':
        faiss_index.create_ivf_index(n_clusters=min(100, len(embeddings) // 100))
        faiss_index.train_index(embeddings)
    else:
        faiss_index.create_index()
    
    # Add embeddings
    faiss_index.add_embeddings(embeddings)
    
    # Save if requested
    if save_path:
        faiss_index.save(save_path)
    
    return faiss_index
