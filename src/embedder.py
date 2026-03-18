"""
Embedding Generation Module
Generate BERT embeddings for documents and queries
"""

import numpy as np
from typing import Union, List
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Embedder:
    """Generate and manage BERT embeddings"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 device: str = None, batch_size: int = 32):
        """
        Initialize embedding generator
        
        Args:
            model_name: Pre-trained Sentence-BERT model
            device: 'cuda' or 'cpu'
            batch_size: Batch size for embedding generation
        """
        self.model_name = model_name
        self.batch_size = batch_size
        
        # Auto-detect device
        import torch
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Loading BERT model: {model_name} on {self.device}")
        self.model = SentenceTransformer(model_name, device=self.device)
        logger.info("Model loaded successfully")
        
        # Get embedding dimension from model
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def generate_embeddings(self, texts: Union[str, List[str]], 
                           show_progress: bool = True,
                           normalize: bool = True) -> np.ndarray:
        """
        Generate embeddings for texts
        
        Args:
            texts: Single text or list of texts
            show_progress: Show progress bar
            normalize: Normalize embeddings (for cosine similarity)
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        
        logger.info(f"Generated embeddings shape: {embeddings.shape}")
        return embeddings
    
    def save_embeddings(self, embeddings: np.ndarray, 
                       output_path: Union[str, Path]):
        """Save embeddings to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        np.save(output_path, embeddings)
        logger.info(f"Embeddings saved to {output_path} ({embeddings.nbytes / 1e6:.2f} MB)")
    
    def load_embeddings(self, input_path: Union[str, Path]) -> np.ndarray:
        """Load embeddings from file"""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Embeddings file not found: {input_path}")
        
        embeddings = np.load(input_path)
        logger.info(f"Loaded embeddings shape: {embeddings.shape}")
        return embeddings
    
    def get_embedding_stats(self, embeddings: np.ndarray) -> dict:
        """Get statistics about embeddings"""
        return {
            'shape': embeddings.shape,
            'dtype': str(embeddings.dtype),
            'size_mb': embeddings.nbytes / 1e6,
            'mean': float(np.mean(embeddings)),
            'std': float(np.std(embeddings)),
            'min': float(np.min(embeddings)),
            'max': float(np.max(embeddings))
        }


def generate_embeddings(texts: List[str], **kwargs) -> np.ndarray:
    """Convenience function to generate embeddings"""
    embedder = Embedder(**kwargs)
    return embedder.generate_embeddings(texts)
