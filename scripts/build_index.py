"""
Script to build embeddings and create FAISS index
"""
import sys
import pickle
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from embeddings.embedding_generator import EmbeddingGenerator, create_embeddings_for_dataset
from vector_database.faiss_index import build_faiss_index, FAISSIndex
from vector_database.index_utils import save_index_metadata, create_document_mapping
from utils.logger import setup_logger
from utils.config import (
    PROCESSED_DATA_DIR,
    EMBEDDINGS_CACHE_FILE,
    FAISS_INDEX_FILE,
    METADATA_FILE
)

logger = setup_logger(__name__)


def main():
    """Main function to build embeddings and FAISS index."""
    
    logger.info("=" * 80)
    logger.info("Starting Embedding Generation and Index Building Pipeline")
    logger.info("=" * 80)
    
    # Step 1: Load processed data
    logger.info("\n[STEP 1] Loading processed data...")
    
    data_file = PROCESSED_DATA_DIR / "stackoverflow_processed.csv"
    
    if not data_file.exists():
        logger.error(f"Processed data file not found: {data_file}")
        logger.info("Please run download_data.py script first!")
        return
    
    df = pd.read_csv(data_file)
    logger.info(f"Loaded {len(df)} documents")
    
    # Extract cleaned text
    if 'cleaned_text' in df.columns:
        texts = df['cleaned_text'].fillna('').astype(str).tolist()
    else:
        texts = df['text'].fillna('').astype(str).tolist()
    
    logger.info(f"Prepared {len(texts)} texts for embedding generation")
    
    # Step 2: Generate embeddings
    logger.info("\n[STEP 2] Generating BERT embeddings...")
    
    embedding_generator = EmbeddingGenerator()
    
    embeddings = embedding_generator.generate_embeddings(
        texts,
        batch_size=32,
        show_progress=True
    )
    
    logger.info(f"Generated embeddings with shape: {embeddings.shape}")
    
    # Save embeddings
    embedding_generator.save_embeddings(embeddings, EMBEDDINGS_CACHE_FILE)
    
    # Step 3: Build FAISS index
    logger.info("\n[STEP 3] Building FAISS index...")
    
    faiss_index = build_faiss_index(
        embeddings=embeddings,
        index_type="IndexFlatL2",  # Use IndexIVFFlat for larger datasets
        metric="cosine",
        save_path=FAISS_INDEX_FILE
    )
    
    logger.info(f"FAISS index built with {faiss_index.index.ntotal} vectors")
    
    # Step 4: Create document metadata mapping
    logger.info("\n[STEP 4] Creating document metadata mapping...")
    
    documents = []
    for idx, row in df.iterrows():
        doc = {
            'text': row.get('cleaned_text', row.get('text', '')),
            'title': row.get('title', ''),
            'metadata': {
                'original_index': idx,
                'text_length': len(row.get('cleaned_text', row.get('text', '')))
            }
        }
        documents.append(doc)
    
    metadata_mapping = create_document_mapping(documents, save=True)
    
    logger.info(f"Created metadata mapping for {len(metadata_mapping)} documents")
    
    # Step 5: Validate index integrity
    logger.info("\n[STEP 5] Validating index integrity...")
    
    assert len(embeddings) == faiss_index.index.ntotal, \
        f"Mismatch: {len(embeddings)} embeddings vs {faiss_index.index.ntotal} indexed"
    
    assert len(metadata_mapping) == faiss_index.index.ntotal, \
        f"Mismatch: {len(metadata_mapping)} metadata entries vs {faiss_index.index.ntotal} indexed"
    
    logger.info("✓ Index integrity validated successfully!")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("Index Building Summary:")
    logger.info("=" * 80)
    logger.info(f"Total Documents: {len(df):,}")
    logger.info(f"Embedding Dimension: {embeddings.shape[1]}")
    logger.info(f"Index Type: {faiss_index.index_type}")
    logger.info(f"Metric: {faiss_index.metric}")
    logger.info(f"\nFiles Created:")
    logger.info(f"  - Embeddings: {EMBEDDINGS_CACHE_FILE}")
    logger.info(f"  - FAISS Index: {FAISS_INDEX_FILE}")
    logger.info(f"  - Metadata: {METADATA_FILE}")
    logger.info("\n" + "=" * 80)
    logger.info("Index building completed successfully!")
    logger.info("=" * 80)
    
    # Test search
    logger.info("\n[TEST SEARCH]")
    logger.info("-" * 80)
    
    test_query = "machine learning algorithms"
    logger.info(f"Test query: '{test_query}'")
    
    # Generate query embedding
    query_embedding = embedding_generator.generate_embeddings(test_query, show_progress=False)
    
    # Search
    distances, indices = faiss_index.search(query_embedding, top_k=5)
    
    logger.info(f"\nTop 5 Results:")
    for i in range(5):
        doc_id = int(indices[0][i])
        score = float(distances[0][i])
        doc_text = metadata_mapping[doc_id]['text'][:100]
        logger.info(f"  {i+1}. Score: {score:.4f} | Text: {doc_text}...")
    
    logger.info("\n" + "=" * 80)
    
    return faiss_index, embeddings, metadata_mapping


if __name__ == "__main__":
    main()
