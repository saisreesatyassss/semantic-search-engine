"""
Script to download and prepare dataset for semantic search
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from preprocessing.data_loader import DataLoader, download_and_prepare_dataset
from preprocessing.text_cleaner import TextCleaner, preprocess_dataset
from utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main function to download and prepare dataset."""
    
    logger.info("=" * 80)
    logger.info("Starting Data Download and Preparation Pipeline")
    logger.info("=" * 80)
    
    # Configuration
    DATASET_NAME = "stackoverflow"
    SAMPLE_SIZE = 10000  # Adjust based on your needs
    
    # Step 1: Download/Load dataset
    logger.info("\n[STEP 1] Loading dataset...")
    df = download_and_prepare_dataset(
        dataset_name=DATASET_NAME,
        sample_size=SAMPLE_SIZE,
        save=True
    )
    
    logger.info(f"Loaded {len(df)} documents")
    logger.info(f"Columns: {list(df.columns)}")
    
    # Step 2: Preprocess text
    logger.info("\n[STEP 2] Preprocessing text data...")
    
    cleaner = TextCleaner(
        lowercase=True,
        remove_punctuation=True,
        remove_stopwords=True,
        remove_special_chars=True,
        remove_numbers=True,
        min_length=10
    )
    
    df = cleaner.clean_dataframe(df, column_name='text', output_column='cleaned_text')
    
    logger.info(f"After preprocessing: {len(df)} documents")
    
    # Step 3: Save processed data
    logger.info("\n[STEP 3] Saving processed data...")
    
    output_file = Path(__file__).parent.parent / "data" / "processed" / f"{DATASET_NAME}_processed.csv"
    df.to_csv(output_file, index=False)
    
    logger.info(f"Saved processed data to: {output_file}")
    
    # Display sample
    logger.info("\n[SAMPLE DATA]")
    logger.info("=" * 80)
    
    for i in range(min(3, len(df))):
        logger.info(f"\nDocument {i+1}:")
        logger.info(f"Original: {df.iloc[i]['text'][:200]}...")
        logger.info(f"Cleaned: {df.iloc[i]['cleaned_text'][:200]}...")
    
    logger.info("\n" + "=" * 80)
    logger.info("Data preparation completed successfully!")
    logger.info("=" * 80)
    
    return df


if __name__ == "__main__":
    main()
