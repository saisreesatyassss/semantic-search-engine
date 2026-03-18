"""
Model loading utilities for Sentence-BERT embeddings
"""
from sentence_transformers import SentenceTransformer
from utils.logger import setup_logger
from utils.config import BERT_MODEL_NAME, DEVICE, EMBEDDING_DIMENSION

logger = setup_logger(__name__)


class ModelLoader:
    """
    Handles loading and configuration of Sentence-BERT models.
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the model loader.
        
        Args:
            model_name: Name of the Sentence-BERT model to load
        """
        self.model_name = model_name or BERT_MODEL_NAME
        self.model = None
        self.device = DEVICE
        self.embedding_dimension = EMBEDDING_DIMENSION
        
        logger.info(f"ModelLoader initialized with model: {self.model_name}")
        logger.info(f"Using device: {self.device}")
    
    def load_model(self) -> SentenceTransformer:
        """
        Load the Sentence-BERT model.
        
        Returns:
            Loaded SentenceTransformer model
        """
        if self.model is not None:
            logger.info("Model already loaded, returning cached instance")
            return self.model
        
        logger.info(f"Loading Sentence-BERT model: {self.model_name}")
        
        try:
            # Load pretrained model
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device
            )
            
            # Set max sequence length
            if hasattr(self.model, 'max_seq_length'):
                self.model.max_seq_length = 256
            
            logger.info(f"Model loaded successfully on {self.device}")
            logger.info(f"Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise RuntimeError(f"Failed to load model: {e}")
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary containing model information
        """
        info = {
            'model_name': self.model_name,
            'device': self.device,
            'embedding_dimension': self.embedding_dimension,
            'max_seq_length': 256
        }
        
        if self.model is not None:
            info['actual_dimension'] = self.model.get_sentence_embedding_dimension()
        
        return info
    
    def unload_model(self) -> None:
        """
        Unload the model from memory to free resources.
        """
        if self.model is not None:
            del self.model
            self.model = None
            
            # Clear CUDA cache if using GPU
            if self.device == 'cuda':
                import torch
                torch.cuda.empty_cache()
            
            logger.info("Model unloaded from memory")


def get_model(model_name: str = None) -> SentenceTransformer:
    """
    Convenience function to get a loaded Sentence-BERT model.
    
    Args:
        model_name: Optional model name override
        
    Returns:
        Loaded SentenceTransformer model
    """
    loader = ModelLoader(model_name)
    return loader.load_model()


# Available recommended models
RECOMMENDED_MODELS = {
    'fast': 'sentence-transformers/all-MiniLM-L6-v2',  # Fast, good quality
    'search': 'sentence-transformers/msmarco-MiniLM-L-6-v3',  # Better for search
    'multilingual': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Multi-language
    'large': 'sentence-transformers/all-mpnet-base-v2'  # Higher quality, slower
}
