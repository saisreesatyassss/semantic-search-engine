"""
Data loading utilities for downloading and processing datasets
"""
import os
import pickle
from pathlib import Path
from typing import Tuple, Optional
import pandas as pd
import numpy as np
from datasets import load_dataset
from utils.logger import setup_logger
from utils.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    SAMPLE_SIZE,
    METADATA_FILE
)

logger = setup_logger(__name__)


class DataLoader:
    """
    Handles downloading and loading of datasets for semantic search.
    """
    
    def __init__(self, dataset_name: str = "stackoverflow"):
        """
        Initialize the data loader.
        
        Args:
            dataset_name: Name of the dataset to load
        """
        self.dataset_name = dataset_name
        self.raw_dir = Path(RAW_DATA_DIR)
        self.processed_dir = Path(PROCESSED_DATA_DIR)
        
        # Ensure directories exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_stackoverflow(self, sample_size: int = None) -> pd.DataFrame:
        """
        Load StackOverflow questions dataset.
        
        Args:
            sample_size: Number of samples to load (None for all)
            
        Returns:
            DataFrame with title and body columns
        """
        sample_size = sample_size or SAMPLE_SIZE
        
        logger.info(f"Loading StackOverflow dataset (sample_size={sample_size})")
        
        try:
            # Load from HuggingFace datasets
            dataset = load_dataset("stackexchange/stackoverflow", split="train")
            
            # Convert to DataFrame
            df = pd.DataFrame(dataset)
            
            # Select relevant columns
            if 'title' in df.columns and 'body' in df.columns:
                df = df[['title', 'body']]
                # Combine title and body
                df['text'] = df['title'].fillna('') + ' ' + df['body'].fillna('')
            elif 'title' in df.columns:
                df = df[['title']]
                df['text'] = df['title']
            else:
                raise ValueError("Dataset doesn't have expected columns")
            
            # Sample if needed
            if sample_size and len(df) > sample_size:
                df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
            
            logger.info(f"Loaded {len(df)} StackOverflow questions")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading StackOverflow dataset: {e}")
            # Fallback to creating sample data
            logger.info("Creating sample dataset instead...")
            return self._create_sample_data(sample_size)
    
    def load_wikipedia(self, sample_size: int = None) -> pd.DataFrame:
        """
        Load Wikipedia articles dataset.
        
        Args:
            sample_size: Number of samples to load
            
        Returns:
            DataFrame with article text
        """
        sample_size = sample_size or SAMPLE_SIZE
        
        logger.info(f"Loading Wikipedia dataset (sample_size={sample_size})")
        
        try:
            # Load simplified Wikipedia dataset
            dataset = load_dataset("wikipedia", "20220301.en", split="train[:10000]")
            
            df = pd.DataFrame(dataset)
            
            if 'text' in df.columns:
                df = df[['text']]
            elif 'article' in df.columns:
                df = df[['article']]
                df.rename(columns={'article': 'text'}, inplace=True)
            
            if sample_size and len(df) > sample_size:
                df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
            
            logger.info(f"Loaded {len(df)} Wikipedia articles")
            return df
            
        except Exception as e:
            logger.error(f"Error loading Wikipedia dataset: {e}")
            return self._create_sample_data(sample_size)
    
    def _create_sample_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """
        Create sample data for testing when real dataset is unavailable.
        
        Args:
            n_samples: Number of samples to create
            
        Returns:
            DataFrame with sample texts
        """
        logger.info(f"Creating {n_samples} sample documents")
        
        # Sample topics for diverse semantic content
        topics = [
            "machine learning algorithms and deep learning neural networks",
            "web development frameworks and frontend backend programming",
            "data science analytics and statistical analysis methods",
            "cloud computing infrastructure and distributed systems",
            "cybersecurity encryption and network protection protocols",
            "mobile application development iOS Android platforms",
            "database management SQL NoSQL data modeling",
            "artificial intelligence natural language processing computer vision",
            "software engineering best practices design patterns",
            "DevOps continuous integration deployment automation",
            "blockchain cryptocurrency decentralized applications",
            "internet things IoT sensors embedded systems",
            "quantum computing physics computational algorithms",
            "bioinformatics genomics protein structure prediction",
            "financial technology trading algorithms risk management"
        ]
        
        # Generate variations
        texts = []
        for i in range(n_samples):
            base_topic = topics[i % len(topics)]
            variation = f"Document {i+1}: Introduction to {base_topic}. "
            variation += f"This comprehensive guide covers advanced concepts in {base_topic.split()[0]} "
            variation += f"and practical applications of {base_topic.split()[-1]}. "
            variation += f"Learn about modern techniques and industry best practices."
            texts.append(variation)
        
        df = pd.DataFrame({'text': texts})
        
        # Save sample data
        sample_path = self.processed_dir / "sample_data.csv"
        df.to_csv(sample_path, index=False)
        logger.info(f"Saved sample data to {sample_path}")
        
        return df
    
    def save_processed_data(
        self,
        df: pd.DataFrame,
        filename: str = "processed_data.csv"
    ) -> Path:
        """
        Save processed DataFrame to disk.
        
        Args:
            df: Processed DataFrame
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        filepath = self.processed_dir / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Saved processed data to {filepath}")
        return filepath
    
    def load_processed_data(self, filename: str = "processed_data.csv") -> pd.DataFrame:
        """
        Load previously processed data from disk.
        
        Args:
            filename: Name of file to load
            
        Returns:
            Loaded DataFrame
        """
        filepath = self.processed_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Processed data file not found: {filepath}")
        
        df = pd.read_csv(filepath)
        logger.info(f"Loaded processed data from {filepath} ({len(df)} rows)")
        return df
    
    def remove_duplicates(self, df: pd.DataFrame, column: str = 'text') -> pd.DataFrame:
        """
        Remove duplicate documents from DataFrame.
        
        Args:
            df: Input DataFrame
            column: Column to check for duplicates
            
        Returns:
            DataFrame with duplicates removed
        """
        initial_count = len(df)
        df = df.drop_duplicates(subset=[column], keep='first')
        final_count = len(df)
        
        logger.info(f"Removed {initial_count - final_count} duplicate documents")
        return df
    
    def filter_by_length(
        self,
        df: pd.DataFrame,
        column: str = 'text',
        min_length: int = 10,
        max_length: int = 5000
    ) -> pd.DataFrame:
        """
        Filter documents by text length.
        
        Args:
            df: Input DataFrame
            column: Text column to filter
            min_length: Minimum character count
            max_length: Maximum character count
            
        Returns:
            Filtered DataFrame
        """
        initial_count = len(df)
        
        # Calculate text lengths
        df['_length'] = df[column].astype(str).str.len()
        
        # Apply filters
        df = df[(df['_length'] >= min_length) & (df['_length'] <= max_length)]
        df = df.drop('_length', axis=1)
        
        final_count = len(df)
        logger.info(f"Filtered {initial_count - final_count} documents by length. "
                   f"Remaining: {final_count}")
        
        return df


def download_and_prepare_dataset(
    dataset_name: str = "stackoverflow",
    sample_size: int = 10000,
    save: bool = True
) -> pd.DataFrame:
    """
    Convenience function to download and prepare a dataset.
    
    Args:
        dataset_name: Name of dataset to load
        sample_size: Number of samples to use
        save: Whether to save processed data
        
    Returns:
        Processed DataFrame
    """
    loader = DataLoader(dataset_name)
    
    # Load raw data
    df = loader.load_stackoverflow(sample_size) if dataset_name == "stackoverflow" \
         else loader.load_wikipedia(sample_size)
    
    # Clean up
    df = loader.remove_duplicates(df)
    df = loader.filter_by_length(df)
    
    # Save if requested
    if save:
        loader.save_processed_data(df, f"{dataset_name}_raw.csv")
    
    return df


def save_metadata(metadata: dict, filename: str = None) -> None:
    """
    Save metadata (document mappings, etc.) to disk.
    
    Args:
        metadata: Dictionary containing metadata
        filename: Output filename
    """
    filename = filename or METADATA_FILE
    with open(filename, 'wb') as f:
        pickle.dump(metadata, f)
    logger.info(f"Saved metadata to {filename}")


def load_metadata(filename: str = None) -> dict:
    """
    Load metadata from disk.
    
    Args:
        filename: Metadata filename
        
    Returns:
        Loaded metadata dictionary
    """
    filename = filename or METADATA_FILE
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Metadata file not found: {filename}")
    
    with open(filename, 'rb') as f:
        metadata = pickle.load(f)
    
    logger.info(f"Loaded metadata from {filename}")
    return metadata
