"""
Data Loading Module
Handles loading and initial processing of raw documents
"""

import pandas as pd
from pathlib import Path
from typing import Union, List
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Load documents from various sources"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        
    def load_csv(self, file_path: Union[str, Path], encoding='utf-8') -> pd.DataFrame:
        """Load documents from CSV file"""
        file_path = self.data_dir / "raw" / file_path if not Path(file_path).is_absolute() else file_path
        
        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path, encoding=encoding)
        
        logger.info(f"Loaded {len(df)} documents with columns: {list(df.columns)}")
        return df
    
    def load_documents(self, source: str = 'local') -> pd.DataFrame:
        """
        Load documents from specified source
        
        Args:
            source: 'local' for local files, 'huggingface' for HF datasets
            
        Returns:
            DataFrame with documents
        """
        if source == 'local':
            return self._load_local_data()
        elif source == 'huggingface':
            return self._load_huggingface_data()
        else:
            raise ValueError(f"Unknown source: {source}")
    
    def _load_local_data(self) -> pd.DataFrame:
        """Load from local data directory"""
        raw_file = self.data_dir / "raw" / "documents.csv"
        
        if raw_file.exists():
            return self.load_csv(raw_file)
        else:
            logger.warning("No local data found, creating sample dataset")
            return self._create_sample_data()
    
    def _load_huggingface_data(self) -> pd.DataFrame:
        """Load from HuggingFace datasets"""
        try:
            from datasets import load_dataset
            
            logger.info("Loading StackOverflow dataset from HuggingFace...")
            dataset = load_dataset("stackexchange/stackoverflow", split="train")
            
            df = dataset.to_pandas()
            df = df[['title', 'body', 'tags']].dropna()
            df['text'] = df['title'] + " " + df['body']
            
            logger.info(f"Loaded {len(df)} documents from HuggingFace")
            return df[['text', 'title', 'tags']]
            
        except Exception as e:
            logger.error(f"Error loading HuggingFace dataset: {e}")
            logger.info("Falling back to sample data")
            return self._create_sample_data()
    
    def _create_sample_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """Create sample technical documents for testing"""
        logger.info(f"Creating {n_samples} sample documents...")
        
        topics = [
            "machine learning", "deep learning", "neural networks",
            "natural language processing", "computer vision",
            "data science", "python programming", "web development",
            "API design", "database optimization", "cloud computing",
            "docker containers", "kubernetes", "microservices",
            "react framework", "javascript", "typescript",
            "SQL queries", "NoSQL databases", "data engineering"
        ]
        
        descriptions = [
            "comprehensive guide to",
            "advanced techniques in",
            "best practices for",
            "introduction to",
            "modern approaches to",
            "industry standards for",
            "cutting-edge developments in",
            "practical applications of"
        ]
        
        documents = []
        for i in range(n_samples):
            topic = topics[i % len(topics)]
            desc = descriptions[i % len(descriptions)]
            
            doc = {
                'id': i,
                'text': f"{desc} {topic} - Document {i}. This covers key concepts, "
                       f"implementation strategies, and real-world examples related to {topic}.",
                'title': f"Guide to {topic.title()} - Part {i}",
                'category': topic,
                'tags': f"{topic},programming,technology"
            }
            documents.append(doc)
        
        df = pd.DataFrame(documents)
        
        # Save to raw data directory
        output_file = self.data_dir / "raw" / "documents.csv"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_file, index=False)
        
        logger.info(f"Sample data saved to {output_file}")
        return df
    
    def save_raw_data(self, df: pd.DataFrame, filename: str = "documents.csv"):
        """Save raw data to file"""
        output_path = self.data_dir / "raw" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Raw data saved to {output_path}")


def load_data(source: str = 'local', **kwargs) -> pd.DataFrame:
    """Convenience function to load data"""
    loader = DataLoader(**kwargs)
    return loader.load_documents(source=source)
