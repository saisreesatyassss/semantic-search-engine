"""
Utilities for FAISS index operations
"""
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.logger import setup_logger
from utils.config import (
    VECTOR_DB_DIR,
    PROCESSED_DATA_DIR,
    FAISS_INDEX_FILE,
    METADATA_FILE
)

logger = setup_logger(__name__)


def save_index_metadata(
    metadata: Dict[str, Any],
    filepath: Optional[Path] = None
) -> Path:
    """
    Save index metadata to disk.
    
    Args:
        metadata: Dictionary containing metadata
        filepath: Output file path
        
    Returns:
        Path to saved file
    """
    filepath = filepath or METADATA_FILE
    filepath = Path(filepath)
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'wb') as f:
        pickle.dump(metadata, f)
    
    logger.info(f"Saved index metadata to {filepath}")
    return filepath


def load_index_metadata(filepath: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load index metadata from disk.
    
    Args:
        filepath: File path to load from
        
    Returns:
        Loaded metadata dictionary
    """
    filepath = filepath or METADATA_FILE
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Metadata file not found: {filepath}")
    
    with open(filepath, 'rb') as f:
        metadata = pickle.load(f)
    
    logger.info(f"Loaded metadata from {filepath}")
    return metadata


def create_document_mapping(
    documents: List[Dict[str, Any]],
    save: bool = True
) -> Dict[int, Dict[str, Any]]:
    """
    Create a mapping from document IDs to document metadata.
    
    Args:
        documents: List of document dictionaries
        save: Whether to save mapping to disk
        
    Returns:
        Dictionary mapping ID to document data
    """
    id_to_doc = {}
    
    for idx, doc in enumerate(documents):
        id_to_doc[idx] = {
            'id': idx,
            'text': doc.get('text', ''),
            'title': doc.get('title', ''),
            'metadata': doc.get('metadata', {})
        }
    
    logger.info(f"Created mapping for {len(id_to_doc)} documents")
    
    if save:
        save_index_metadata(id_to_doc)
    
    return id_to_doc


def get_document_by_id(
    doc_id: int,
    metadata_file: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Retrieve a document by its ID.
    
    Args:
        doc_id: Document ID
        metadata_file: Metadata file path
        
    Returns:
        Document dictionary
    """
    metadata = load_index_metadata(metadata_file)
    
    if doc_id not in metadata:
        raise KeyError(f"Document ID {doc_id} not found")
    
    return metadata[doc_id]


def get_documents_by_ids(
    doc_ids: List[int],
    metadata_file: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve multiple documents by their IDs.
    
    Args:
        doc_ids: List of document IDs
        metadata_file: Metadata file path
        
    Returns:
        List of document dictionaries
    """
    metadata = load_index_metadata(metadata_file)
    
    documents = []
    for doc_id in doc_ids:
        if doc_id in metadata:
            documents.append(metadata[doc_id])
        else:
            logger.warning(f"Document ID {doc_id} not found in metadata")
    
    return documents


def format_search_results(
    distances: np.ndarray,
    indices: np.ndarray,
    metadata: Dict[int, Dict[str, Any]],
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Format search results with document information and scores.
    
    Args:
        distances: Distance/similarity scores from FAISS
        indices: Document indices from FAISS
        metadata: Document metadata mapping
        top_k: Number of results to format
        
    Returns:
        List of formatted result dictionaries
    """
    results = []
    
    # Get actual number of results (may be less than top_k)
    n_results = min(top_k, len(indices[0]))
    
    for i in range(n_results):
        doc_id = int(indices[0][i])
        
        # Skip invalid IDs
        if doc_id < 0 or doc_id >= len(metadata):
            continue
        
        # Get document info
        doc_info = metadata.get(doc_id, {})
        
        # Convert distance to similarity score (for cosine similarity)
        # Higher distance = lower similarity for L2, but higher = better for IP with normalized vectors
        similarity_score = float(distances[0][i])
        
        result = {
            'rank': i + 1,
            'document_id': doc_id,
            'text': doc_info.get('text', ''),
            'title': doc_info.get('title', ''),
            'similarity_score': similarity_score,
            'metadata': doc_info.get('metadata', {})
        }
        
        results.append(result)
    
    logger.info(f"Formatted {len(results)} search results")
    
    return results


def validate_index_integrity(
    embeddings_file: Path,
    index_file: Optional[Path] = None
) -> bool:
    """
    Validate that the index has the same number of vectors as embeddings.
    
    Args:
        embeddings_file: Path to embeddings file
        index_file: Path to FAISS index file
        
    Returns:
        True if integrity check passes
    """
    import faiss
    
    index_file = index_file or FAISS_INDEX_FILE
    
    # Load embeddings to check count
    embeddings = np.load(embeddings_file)
    n_embeddings = len(embeddings)
    
    # Load index
    if not index_file.exists():
        logger.error(f"Index file not found: {index_file}")
        return False
    
    index = faiss.read_index(str(index_file))
    n_indexed = index.ntotal
    
    if n_embeddings != n_indexed:
        logger.error(f"Integrity check failed: {n_embeddings} embeddings vs {n_indexed} indexed")
        return False
    
    logger.info(f"Integrity check passed: {n_embeddings} vectors in both embeddings and index")
    return True


def get_index_statistics(index_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Get statistics about the FAISS index.
    
    Args:
        index_file: Path to index file
        
    Returns:
        Dictionary of index statistics
    """
    import faiss
    
    index_file = index_file or FAISS_INDEX_FILE
    
    if not index_file.exists():
        return {}
    
    index = faiss.read_index(str(index_file))
    
    stats = {
        'total_vectors': index.ntotal,
        'dimension': index.d,
        'index_type': type(index).__name__
    }
    
    # Additional stats for IVF indexes
    if hasattr(index, 'nlist'):
        stats['n_clusters'] = index.nlist
    
    if hasattr(index, 'nprobe'):
        stats['nprobe'] = index.nprobe
    
    return stats


def optimize_index_for_search(
    index_file: Optional[Path] = None,
    nprobe: int = None
) -> None:
    """
    Optimize index search parameters.
    
    Args:
        index_file: Path to index file
        nprobe: Number of clusters to search (for IVF indexes)
    """
    import faiss
    
    index_file = index_file or FAISS_INDEX_FILE
    
    if not index_file.exists():
        return
    
    index = faiss.read_index(str(index_file))
    
    # Set nprobe for IVF indexes
    if hasattr(index, 'nprobe') and nprobe:
        index.nprobe = nprobe
        logger.info(f"Set nprobe to {nprobe}")
        
        # Save optimized index
        faiss.write_index(index, str(index_file))
        logger.info("Saved optimized index")
