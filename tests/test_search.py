"""
Test suite for Semantic Search Engine
"""
import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from preprocessing.text_cleaner import TextCleaner
from embeddings.embedding_generator import EmbeddingGenerator
from vector_database.faiss_index import FAISSIndex, build_faiss_index


class TestTextCleaner:
    """Test text cleaning functionality."""
    
    def test_lowercase(self):
        """Test lowercase conversion."""
        cleaner = TextCleaner(lowercase=True, remove_stopwords=False)
        text = "HELLO WORLD"
        cleaned = cleaner.clean_text(text)
        assert cleaned == "hello world"
    
    def test_remove_punctuation(self):
        """Test punctuation removal."""
        cleaner = TextCleaner(remove_punctuation=True, remove_stopwords=False)
        text = "Hello, world! How are you?"
        cleaned = cleaner.clean_text(text)
        assert "," not in cleaned
        assert "!" not in cleaned
        assert "?" not in cleaned
    
    def test_remove_stopwords(self):
        """Test stopword removal."""
        cleaner = TextCleaner(remove_stopwords=True)
        text = "the quick brown fox jumps over the lazy dog"
        cleaned = cleaner.clean_text(text)
        assert "the" not in cleaned
        assert len(cleaned) < len(text)
    
    def test_remove_urls(self):
        """Test URL removal."""
        cleaner = TextCleaner(remove_special_chars=True, remove_stopwords=False)
        text = "Check this out https://example.com/page"
        cleaned = cleaner.clean_text(text)
        assert "https://" not in cleaned
        assert "example.com" not in cleaned
    
    def test_min_length_filter(self):
        """Test minimum length filtering."""
        cleaner = TextCleaner(min_length=10, remove_stopwords=False)
        text = "Hi there"
        cleaned = cleaner.clean_text(text)
        assert cleaned == ""  # Too short
    
    def test_clean_dataframe(self):
        """Test dataframe cleaning."""
        import pandas as pd
        
        cleaner = TextCleaner(remove_stopwords=False)
        df = pd.DataFrame({'text': ['Hello World', 'Short', 'Another Example']})
        cleaned_df = cleaner.clean_dataframe(df, 'text')
        
        assert 'cleaned_text' in cleaned_df.columns
        assert len(cleaned_df) <= len(df)


class TestEmbeddingGenerator:
    """Test embedding generation."""
    
    @pytest.fixture
    def generator(self):
        """Create embedding generator."""
        return EmbeddingGenerator(model_name='sentence-transformers/all-MiniLM-L6-v2')
    
    def test_single_embedding(self, generator):
        """Test single text embedding."""
        text = "This is a test sentence."
        embedding = generator.generate_embeddings(text, show_progress=False)
        
        assert embedding.shape[0] == 1
        assert embedding.shape[1] == generator.get_embedding_dimension()
    
    def test_batch_embeddings(self, generator):
        """Test batch embedding generation."""
        texts = [
            "First test sentence",
            "Second test sentence",
            "Third test sentence"
        ]
        embeddings = generator.generate_embeddings(texts, show_progress=False)
        
        assert embeddings.shape[0] == 3
        assert embeddings.shape[1] == generator.get_embedding_dimension()
    
    def test_embedding_normalization(self, generator):
        """Test that embeddings are normalized."""
        text = "Test normalization"
        embedding = generator.generate_embeddings(text, show_progress=False)
        
        # Normalized vectors should have unit norm
        norm = np.linalg.norm(embedding[0])
        assert np.isclose(norm, 1.0, atol=1e-5)
    
    def test_save_load_embeddings(self, generator, tmp_path):
        """Test saving and loading embeddings."""
        texts = ["Test sentence"]
        embeddings = generator.generate_embeddings(texts, show_progress=False)
        
        # Save
        save_path = generator.save_embeddings(embeddings, tmp_path / "test.npy")
        assert save_path.exists()
        
        # Load
        loaded = generator.load_embeddings(tmp_path / "test.npy")
        assert np.array_equal(embeddings, loaded)


class TestFAISSIndex:
    """Test FAISS index operations."""
    
    @pytest.fixture
    def sample_embeddings(self):
        """Generate sample embeddings for testing."""
        np.random.seed(42)
        return np.random.rand(100, 384).astype(np.float32)
    
    def test_create_index(self, sample_embeddings):
        """Test index creation."""
        dim = sample_embeddings.shape[1]
        faiss_idx = FAISSIndex(embedding_dim=dim)
        index = faiss_idx.create_index()
        
        assert index is not None
        assert index.d == dim
    
    def test_add_embeddings(self, sample_embeddings):
        """Test adding embeddings to index."""
        dim = sample_embeddings.shape[1]
        faiss_idx = FAISSIndex(embedding_dim=dim)
        faiss_idx.create_index()
        faiss_idx.add_embeddings(sample_embeddings)
        
        assert faiss_idx.index.ntotal == len(sample_embeddings)
    
    def test_search(self, sample_embeddings):
        """Test similarity search."""
        dim = sample_embeddings.shape[1]
        faiss_idx = FAISSIndex(embedding_dim=dim, metric='cosine')
        faiss_idx.create_index()
        faiss_idx.add_embeddings(sample_embeddings)
        
        # Use first embedding as query
        query = sample_embeddings[0]
        distances, indices = faiss_idx.search(query, top_k=5)
        
        assert len(distances[0]) == 5
        assert len(indices[0]) == 5
        assert indices[0][0] == 0  # Should find itself as closest
    
    def test_save_load_index(self, sample_embeddings, tmp_path):
        """Test saving and loading index."""
        dim = sample_embeddings.shape[1]
        faiss_idx = FAISSIndex(embedding_dim=dim)
        faiss_idx.create_index()
        faiss_idx.add_embeddings(sample_embeddings)
        
        # Save
        save_path = tmp_path / "test.index"
        faiss_idx.save(save_path)
        assert save_path.exists()
        
        # Load
        faiss_idx_loaded = FAISSIndex(embedding_dim=dim)
        faiss_idx_loaded.load(save_path)
        
        assert faiss_idx_loaded.index.ntotal == faiss_idx.index.ntotal
    
    def test_build_faiss_index_helper(self, sample_embeddings):
        """Test build_faiss_index helper function."""
        faiss_idx = build_faiss_index(
            embeddings=sample_embeddings,
            index_type='IndexFlatL2',
            metric='cosine'
        )
        
        assert faiss_idx.index.ntotal == len(sample_embeddings)
        assert faiss_idx.is_trained


class TestIntegration:
    """Integration tests for complete pipeline."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for integration testing."""
        texts = [
            "Machine learning algorithms for data analysis",
            "Deep learning neural networks architecture",
            "Natural language processing applications",
            "Computer vision image recognition systems",
            "Reinforcement learning agent training"
        ]
        return texts
    
    def test_end_to_end_pipeline(self, sample_data):
        """Test complete pipeline from text to search."""
        # Generate embeddings
        generator = EmbeddingGenerator()
        embeddings = generator.generate_embeddings(sample_data, show_progress=False)
        
        # Build index
        faiss_idx = build_faiss_index(embeddings, metric='cosine')
        
        # Create document mapping
        doc_mapping = {
            i: {'text': text, 'id': i}
            for i, text in enumerate(sample_data)
        }
        
        # Test search
        query = "machine learning algorithms"
        query_emb = generator.generate_embeddings(query, show_progress=False)
        distances, indices = faiss_idx.search(query_emb, top_k=3)
        
        # Validate results
        assert len(distances[0]) == 3
        assert len(indices[0]) == 3
        assert all(idx >= 0 for idx in indices[0])
        
        # First result should be most relevant
        assert distances[0][0] >= distances[0][1] >= distances[0][2]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
