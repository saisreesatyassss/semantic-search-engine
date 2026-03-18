"""
Embedding generation using Sentence-BERT
"""
import numpy as np
from typing import List, Union, Optional
from tqdm import tqdm
import joblib
from pathlib import Path

from sentence_transformers import SentenceTransformer
from utils.logger import setup_logger
from utils.config import (
    BATCH_SIZE,
    EMBEDDINGS_CACHE_FILE,
    DEVICE
)
from .model_loader import ModelLoader

logger = setup_logger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings for text documents using Sentence-BERT.
    """
    
    def __init__(
        self,
        model_name: str = None,
        batch_size: int = None,
        device: str = None
    ):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of Sentence-BERT model to use
            batch_size: Batch size for embedding generation
            device: Device to run inference on ('cuda' or 'cpu')
        """
        self.model_loader = ModelLoader(model_name)
        self.model = self.model_loader.load_model()
        self.batch_size = batch_size or BATCH_SIZE
        self.device = device or DEVICE
        
        logger.info(f"EmbeddingGenerator initialized with batch_size={batch_size}, "
                   f"device={self.device}")
    
    def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        batch_size: int = None,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for one or more texts.
        
        Args:
            texts: Single text string or list of text strings
            batch_size: Override default batch size
            show_progress: Show progress bar
            
        Returns:
            Numpy array of embeddings
        """
        # Convert single text to list
        if isinstance(texts, str):
            texts = [texts]
        
        batch_size = batch_size or self.batch_size
        
        logger.info(f"Generating embeddings for {len(texts)} texts with batch_size={batch_size}")
        
        try:
            # Generate embeddings using Sentence-BERT
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True  # Normalize for cosine similarity
            )
            
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}")
    
    def generate_embeddings_batched(
        self,
        texts: List[str],
        batch_size: int = None,
        output_file: Optional[Path] = None
    ) -> np.ndarray:
        """
        Generate embeddings in batches for very large datasets.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            output_file: Optional file to save intermediate results
            
        Returns:
            Numpy array of all embeddings
        """
        batch_size = batch_size or self.batch_size
        n_texts = len(texts)
        n_batches = (n_texts + batch_size - 1) // batch_size
        
        logger.info(f"Processing {n_texts} texts in {n_batches} batches")
        
        all_embeddings = []
        
        for i in tqdm(range(n_batches), desc="Generating embeddings"):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, n_texts)
            batch_texts = texts[start_idx:end_idx]
            
            # Generate embeddings for batch
            batch_embeddings = self.generate_embeddings(
                batch_texts,
                batch_size=batch_size,
                show_progress=False
            )
            
            all_embeddings.append(batch_embeddings)
            
            # Save intermediate results if requested
            if output_file and (i + 1) % 10 == 0:
                temp_embeddings = np.vstack(all_embeddings)
                np.save(output_file, temp_embeddings)
                logger.info(f"Saved intermediate embeddings: {temp_embeddings.shape}")
        
        # Combine all embeddings
        final_embeddings = np.vstack(all_embeddings)
        
        logger.info(f"Final embeddings shape: {final_embeddings.shape}")
        
        return final_embeddings
    
    def save_embeddings(
        self,
        embeddings: np.ndarray,
        filepath: Union[str, Path] = None
    ) -> Path:
        """
        Save embeddings to disk.
        
        Args:
            embeddings: Embeddings array to save
            filepath: Output file path (default: from config)
            
        Returns:
            Path to saved file
        """
        filepath = filepath or EMBEDDINGS_CACHE_FILE
        filepath = Path(filepath)
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save embeddings
        np.save(filepath, embeddings)
        
        logger.info(f"Saved embeddings to {filepath} (shape: {embeddings.shape})")
        
        return filepath
    
    def load_embeddings(
        self,
        filepath: Union[str, Path] = None
    ) -> np.ndarray:
        """
        Load embeddings from disk.
        
        Args:
            filepath: File path to load from
            
        Returns:
            Loaded embeddings array
        """
        filepath = filepath or EMBEDDINGS_CACHE_FILE
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Embeddings file not found: {filepath}")
        
        embeddings = np.load(filepath)
        logger.info(f"Loaded embeddings from {filepath} (shape: {embeddings.shape})")
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of generated embeddings.
        
        Returns:
            Embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()


def create_embeddings_for_dataset(
    texts: List[str],
    model_name: str = None,
    batch_size: int = None,
    save: bool = True,
    output_file: Path = None
) -> np.ndarray:
    """
    Convenience function to create embeddings for a dataset.
    
    Args:
        texts: List of texts to embed
        model_name: Optional model name override
        batch_size: Batch size for encoding
        save: Whether to save embeddings to disk
        output_file: Output file path
        
    Returns:
        Generated embeddings array
    """
    generator = EmbeddingGenerator(model_name=model_name, batch_size=batch_size)
    
    # Generate embeddings
    embeddings = generator.generate_embeddings(texts, show_progress=True)
    
    # Save if requested
    if save:
        generator.save_embeddings(embeddings, output_file)
    
    return embeddings


def load_or_create_embeddings(
    texts: List[str],
    cache_file: Path = None,
    model_name: str = None,
    force_recreate: bool = False
) -> np.ndarray:
    """
    Load cached embeddings or create new ones if cache doesn't exist.
    
    Args:
        texts: Texts to create embeddings for
        cache_file: Cache file path
        model_name: Model to use
        force_recreate: Force recreation even if cache exists
        
    Returns:
        Embeddings array
    """
    cache_file = cache_file or EMBEDDINGS_CACHE_FILE
    cache_file = Path(cache_file)
    
    # Try to load cached embeddings
    if cache_file.exists() and not force_recreate:
        logger.info(f"Loading cached embeddings from {cache_file}")
        try:
            return np.load(cache_file)
        except Exception as e:
            logger.warning(f"Error loading cached embeddings: {e}")
    
    # Create new embeddings
    logger.info("Creating new embeddings...")
    embeddings = create_embeddings_for_dataset(
        texts,
        model_name=model_name,
        save=True,
        output_file=cache_file
    )
    
    return embeddings
