"""
Main Entry Point for Semantic Search Engine
Command-line interface and pipeline execution
"""

import argparse
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import setup_logging, load_config, ensure_directories
from src.data_loader import DataLoader
from src.preprocess import TextPreprocessor
from src.embedder import Embedder
from src.build_index import FAISSIndexBuilder, create_document_mapping
from src.search import SemanticSearch


def build_pipeline(config: dict):
    """
    Build complete search pipeline from raw data
    
    Args:
        config: Configuration dictionary
    """
    logger = logging.getLogger(__name__)
    
    # Step 1: Load data
    logger.info("=" * 60)
    logger.info("STEP 1: Loading Data")
    logger.info("=" * 60)
    
    loader = DataLoader()
    df = loader.load_documents(source='local')
    logger.info(f"Loaded {len(df)} documents")
    
    # Save raw data
    loader.save_raw_data(df, "documents.csv")
    
    # Step 2: Preprocess text
    logger.info("=" * 60)
    logger.info("STEP 2: Preprocessing Text")
    logger.info("=" * 60)
    
    preprocessor = TextPreprocessor({
        'lowercase': True,
        'remove_punctuation': True,
        'remove_stopwords': True,
        'remove_special_chars': True,
        'min_length': 10
    })
    
    df = preprocessor.clean_dataframe(df, 'text', 'cleaned_text')
    
    # Save processed data
    output_file = Path(config['data']['processed_dir']) / "cleaned_documents.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    logger.info(f"Processed data saved to {output_file}")
    
    # Step 3: Generate embeddings
    logger.info("=" * 60)
    logger.info("STEP 3: Generating BERT Embeddings")
    logger.info("=" * 60)
    
    embedder = Embedder(
        model_name=config['model']['name'],
        batch_size=config['model']['batch_size'],
        device=config['model']['device']
    )
    
    texts = df['cleaned_text'].fillna('').tolist()
    embeddings = embedder.generate_embeddings(texts, show_progress=True)
    
    # Save embeddings
    embeddings_file = Path(config['data']['embeddings_file'])
    embedder.save_embeddings(embeddings, embeddings_file)
    
    # Step 4: Build FAISS index
    logger.info("=" * 60)
    logger.info("STEP 4: Building FAISS Index")
    logger.info("=" * 60)
    
    faiss_builder = FAISSIndexBuilder(
        embedding_dim=embedder.embedding_dim,
        index_type=config['faiss']['index_type'],
        metric=config['faiss']['metric']
    )
    
    faiss_builder.build_index(embeddings)
    
    # Save index
    index_file = Path(config['data']['index_file'])
    faiss_builder.save_index(index_file)
    
    # Step 5: Create document mapping
    logger.info("=" * 60)
    logger.info("STEP 5: Creating Document Mapping")
    logger.info("=" * 60)
    
    documents = df.to_dict('records')
    metadata_file = Path(config['data']['metadata_file'])
    doc_mapping = create_document_mapping(documents, metadata_file)
    
    # Summary
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"Total documents: {len(df)}")
    logger.info(f"Embedding dimension: {embedder.embedding_dim}")
    logger.info(f"Index type: {config['faiss']['index_type']}")
    logger.info(f"Files created:")
    logger.info(f"  - {embeddings_file}")
    logger.info(f"  - {index_file}")
    logger.info(f"  - {metadata_file}")
    
    return {
        'df': df,
        'embeddings': embeddings,
        'faiss_index': faiss_builder.index,
        'doc_mapping': doc_mapping,
        'embedder': embedder
    }


def run_search(query: str, config: dict, top_k: int = 10, threshold: float = 0.5):
    """
    Run semantic search on existing index
    
    Args:
        query: Search query
        config: Configuration dictionary
        top_k: Number of results
        threshold: Similarity threshold
    """
    logger = logging.getLogger(__name__)
    
    # Load existing components
    embedder = Embedder(
        model_name=config['model']['name'],
        device=config['model']['device']
    )
    
    faiss_builder = FAISSIndexBuilder(
        embedding_dim=embedder.embedding_dim,
        index_type=config['faiss']['index_type'],
        metric=config['faiss']['metric']
    )
    
    index_file = Path(config['data']['index_file'])
    faiss_builder.load_index(index_file)
    
    # Load document mapping
    from src.build_index import load_document_mapping
    metadata_file = Path(config['data']['metadata_file'])
    doc_mapping = load_document_mapping(metadata_file)
    
    # Initialize search engine
    search_engine = SemanticSearch(
        faiss_index=faiss_builder,
        embedder=embedder,
        doc_mapping=doc_mapping
    )
    
    # Perform search
    results = search_engine.search(query, top_k=top_k, threshold=threshold)
    
    # Display results
    print("\n" + "=" * 80)
    print(f"SEARCH RESULTS FOR: '{query}'")
    print("=" * 80)
    
    if not results:
        print("No results found.")
        return
    
    for result in results:
        print(f"\n[Rank #{result['rank']}] Score: {result['similarity_score']:.4f}")
        print(f"Document ID: {result['document_id']}")
        if result.get('title'):
            print(f"Title: {result['title']}")
        print(f"Text: {result['text'][:300]}...")
        print("-" * 80)
    
    print(f"\nTotal results: {len(results)}")


def main():
    """Main entry point with CLI"""
    parser = argparse.ArgumentParser(
        description="Semantic Search Engine using BERT and FAISS"
    )
    
    parser.add_argument(
        '--build',
        action='store_true',
        help='Build the complete search pipeline'
    )
    
    parser.add_argument(
        '--search',
        type=str,
        help='Search query string'
    )
    
    parser.add_argument(
        '--top-k',
        type=int,
        default=10,
        help='Number of results to return (default: 10)'
    )
    
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.5,
        help='Similarity threshold (default: 0.5)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Setup
    config = load_config(args.config)
    ensure_directories()
    logger = setup_logging(config['logging']['file'], config['logging']['level'])
    
    logger.info("Semantic Search Engine Started")
    logger.info(f"Configuration loaded from: {args.config}")
    
    # Execute requested operation
    if args.build:
        build_pipeline(config)
    elif args.search:
        run_search(args.search, config, top_k=args.top_k, threshold=args.threshold)
    else:
        parser.print_help()
    
    logger.info("Application finished")


if __name__ == "__main__":
    main()
