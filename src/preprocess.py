"""
Text Preprocessing Module
Clean and normalize text data for embedding generation
"""

import re
import pandas as pd
from typing import List, Union
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """Advanced text cleaning and normalization"""
    
    def __init__(self, config: dict = None):
        self.config = config or {
            'lowercase': True,
            'remove_punctuation': True,
            'remove_stopwords': True,
            'remove_special_chars': True,
            'remove_numbers': False,
            'min_length': 10
        }
        
        # Download required NLTK data
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            import nltk
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            self.stop_words = set(stopwords.words('english'))
    
    def clean_text(self, text: str) -> str:
        """
        Clean a single text string
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned and normalized text
        """
        if not isinstance(text, str) or len(text.strip()) == 0:
            return ""
        
        # Lowercase conversion
        if self.config.get('lowercase', True):
            text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters (keep alphanumeric and spaces)
        if self.config.get('remove_special_chars', True):
            text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove numbers if configured
        if self.config.get('remove_numbers', False):
            text = re.sub(r'\d+', '', text)
        
        # Remove punctuation
        if self.config.get('remove_punctuation', True):
            text = re.sub(r'[^\w\s]', '', text)
        
        # Tokenize and remove stopwords
        if self.config.get('remove_stopwords', True):
            tokens = word_tokenize(text)
            tokens = [word for word in tokens if word not in self.stop_words]
            text = ' '.join(tokens)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Apply minimum length filter
        if len(text) < self.config.get('min_length', 10):
            return ""
        
        return text
    
    def clean_dataframe(self, df: pd.DataFrame, 
                       input_column: str = 'text',
                       output_column: str = 'cleaned_text') -> pd.DataFrame:
        """
        Clean text column in DataFrame
        
        Args:
            df: Input DataFrame
            input_column: Column containing raw text
            output_column: Column name for cleaned text
            
        Returns:
            DataFrame with cleaned text
        """
        logger.info(f"Cleaning {len(df)} documents...")
        
        df[output_column] = df[input_column].apply(self.clean_text)
        
        # Remove empty rows
        original_count = len(df)
        df = df[df[output_column].str.len() > 0]
        removed_count = original_count - len(df)
        
        logger.info(f"Removed {removed_count} empty documents ({removed_count/original_count*100:.1f}%)")
        logger.info(f"Final dataset: {len(df)} documents")
        
        return df.reset_index(drop=True)
    
    def batch_clean(self, texts: List[str], show_progress: bool = True) -> List[str]:
        """
        Clean multiple texts with optional progress tracking
        
        Args:
            texts: List of text strings
            show_progress: Whether to show progress bar
            
        Returns:
            List of cleaned texts
        """
        from tqdm import tqdm
        
        cleaned = []
        iterator = tqdm(texts) if show_progress else texts
        
        for text in iterator:
            cleaned.append(self.clean_text(text))
        
        return cleaned


def preprocess_text(text: str, **kwargs) -> str:
    """Convenience function to clean a single text"""
    preprocessor = TextPreprocessor(kwargs)
    return preprocessor.clean_text(text)


def preprocess_dataframe(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Convenience function to clean a DataFrame"""
    preprocessor = TextPreprocessor(kwargs)
    return preprocessor.clean_dataframe(df)
