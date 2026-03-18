"""
Text cleaning and normalization utilities for semantic search
"""
import re
import string
from typing import List, Union
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd

# Download required NLTK resources
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')

from utils.logger import setup_logger

logger = setup_logger(__name__)


class TextCleaner:
    """
    A comprehensive text cleaning class for preprocessing documents.
    """
    
    def __init__(
        self,
        lowercase: bool = True,
        remove_punctuation: bool = True,
        remove_stopwords: bool = True,
        remove_special_chars: bool = True,
        remove_numbers: bool = True,
        min_length: int = 10
    ):
        """
        Initialize the TextCleaner with configuration options.
        
        Args:
            lowercase: Convert text to lowercase
            remove_punctuation: Remove punctuation marks
            remove_stopwords: Remove common English stopwords
            remove_special_chars: Remove special characters and URLs
            remove_numbers: Remove numerical digits
            min_length: Minimum length of text to keep
        """
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation
        self.remove_stopwords = remove_stopwords
        self.remove_special_chars = remove_special_chars
        self.remove_numbers = remove_numbers
        self.min_length = min_length
        
        # Load English stopwords
        self.stop_words = set(stopwords.words('english'))
        
        logger.info(f"TextCleaner initialized with lowercase={lowercase}, "
                   f"remove_punctuation={remove_punctuation}, "
                   f"remove_stopwords={remove_stopwords}")
    
    def clean_text(self, text: str) -> str:
        """
        Apply all cleaning operations to a single text.
        
        Args:
            text: Input text string
            
        Returns:
            Cleaned text string
        """
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        if self.lowercase:
            text = text.lower()
        
        # Remove URLs
        if self.remove_special_chars:
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove mentions and hashtags (for social media text)
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove numbers
        if self.remove_numbers:
            text = re.sub(r'\d+', '', text)
        
        # Remove special characters
        if self.remove_special_chars:
            text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove punctuation
        if self.remove_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize and remove stopwords
        if self.remove_stopwords:
            tokens = word_tokenize(text)
            tokens = [word for word in tokens if word not in self.stop_words]
            text = ' '.join(tokens)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Check minimum length
        if len(text) < self.min_length:
            return ""
        
        return text
    
    def clean_dataframe(
        self,
        df: pd.DataFrame,
        column_name: str,
        output_column: str = 'cleaned_text'
    ) -> pd.DataFrame:
        """
        Clean text data in a pandas DataFrame.
        
        Args:
            df: Input DataFrame
            column_name: Name of column containing text to clean
            output_column: Name of output column for cleaned text
            
        Returns:
            DataFrame with cleaned text
        """
        logger.info(f"Cleaning {len(df)} documents in column '{column_name}'")
        
        # Apply cleaning function
        df[output_column] = df[column_name].apply(self.clean_text)
        
        # Remove empty rows
        initial_count = len(df)
        df = df[df[output_column] != ""]
        final_count = len(df)
        
        logger.info(f"Removed {initial_count - final_count} empty/short documents. "
                   f"Remaining: {final_count}")
        
        return df
    
    def clean_batch(self, texts: List[str]) -> List[str]:
        """
        Clean a batch of texts efficiently.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of cleaned text strings
        """
        logger.info(f"Cleaning batch of {len(texts)} texts")
        return [self.clean_text(text) for text in texts]


def normalize_text(text: str) -> str:
    """
    Quick function to normalize text with default settings.
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    cleaner = TextCleaner()
    return cleaner.clean_text(text)


def preprocess_dataset(
    df: pd.DataFrame,
    text_column: str = 'text',
    output_column: str = 'cleaned_text'
) -> pd.DataFrame:
    """
    Preprocess an entire dataset with default cleaning parameters.
    
    Args:
        df: Input DataFrame
        text_column: Column name containing raw text
        output_column: Column name for cleaned text
        
    Returns:
        Processed DataFrame
    """
    cleaner = TextCleaner(
        lowercase=True,
        remove_punctuation=True,
        remove_stopwords=True,
        remove_special_chars=True,
        remove_numbers=True,
        min_length=10
    )
    
    return cleaner.clean_dataframe(df, text_column, output_column)
