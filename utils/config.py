"""
Configuration constants for the Semantic Search Engine
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
SAVED_MODELS_DIR = MODELS_DIR / "saved_models"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_database"

# Model configurations
BERT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# Alternative: "sentence-transformers/msmarco-MiniLM-L-6-v3"
EMBEDDING_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2
MAX_SEQ_LENGTH = 256
BATCH_SIZE = 32

# FAISS configurations
FAISS_INDEX_TYPE = "IndexFlatL2"  # Options: IndexFlatL2, IndexIVFFlat
FAISS_NPROBE = 5  # Number of clusters to search for IVF index
FAISS_METRIC = "cosine"  # Options: cosine, L2

# Search configurations
TOP_K_RESULTS = 10
SIMILARITY_THRESHOLD = 0.3

# Preprocessing configurations
REMOVE_STOPWORDS = True
REMOVE_PUNCTUATION = True
LOWERCASE = True
MIN_TEXT_LENGTH = 10

# API configurations
API_HOST = "0.0.0.0"
API_PORT = 8000
API_DEBUG = True

# Streamlit configurations
STREAMLIT_PORT = 8501

# Logging configurations
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = PROJECT_ROOT / "logs" / "semantic_search.log"

# Dataset configurations (for StackOverflow dataset)
DATASET_SOURCE = "stackoverflow"
DATASET_URL = "https://huggingface.co/datasets/stackexchange/stackoverflow"
SAMPLE_SIZE = 10000  # Number of samples to use for demo

# Cache configurations
CACHE_DIR = PROJECT_ROOT / ".cache"
EMBEDDINGS_CACHE_FILE = PROCESSED_DATA_DIR / "embeddings.npy"
FAISS_INDEX_FILE = VECTOR_DB_DIR / "faiss.index"
METADATA_FILE = PROCESSED_DATA_DIR / "metadata.pkl"

# Device configuration
import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
