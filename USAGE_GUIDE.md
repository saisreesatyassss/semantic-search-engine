# 🎓 Complete Usage Guide

## Semantic Search Engine using BERT and FAISS

This comprehensive guide covers all aspects of using the Semantic Search Engine.

---

## 📖 Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Python API Usage](#python-api-usage)
4. [REST API Usage](#rest-api-usage)
5. [Web Interface Usage](#web-interface-usage)
6. [Advanced Configuration](#advanced-configuration)
7. [Customization Examples](#customization-examples)
8. [Performance Tuning](#performance-tuning)
9. [Troubleshooting](#troubleshooting)

---

## 🔧 Installation

### Prerequisites

- Python 3.9 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Internet connection (for model download)

### Windows Setup

```cmd
cd semantic-search-engine
setup.bat
```

### Linux/Mac Setup

```bash
cd semantic-search-engine
chmod +x setup.sh
./setup.sh
```

### Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
```

---

## ⚡ Quick Start

### Step-by-Step (First Time)

```bash
# 1. Prepare dataset
python scripts/download_data.py

# 2. Build search index
python scripts/build_index.py

# 3. Start API server
uvicorn api.main:app --reload

# 4. (Optional) Start web UI in new terminal
streamlit run web_app/app.py
```

### Subsequent Runs

Once the index is built, you only need to:

```bash
# Start API server
uvicorn api.main:app --reload

# Access at http://localhost:8000
```

---

## 💻 Python API Usage

### Basic Search

```python
from search_engine import SemanticSearchEngine

# Initialize
engine = SemanticSearchEngine()
engine.initialize()

# Search
results = engine.search(
    query="deep learning for image classification",
    top_k=10,
    threshold=0.5
)

# Display results
for result in results:
    print(f"Rank {result['rank']}: {result['similarity_score']:.3f}")
    print(f"Text: {result['text'][:200]}...")
    print("-" * 80)
```

### Batch Search

```python
queries = [
    "machine learning algorithms",
    "neural network architectures",
    "natural language processing"
]

all_results = engine.search_batch(queries, top_k=5)

for i, results in enumerate(all_results):
    print(f"\nQuery {i+1}: {queries[i]}")
    for result in results:
        print(f"  {result['rank']}. Score: {result['similarity_score']:.3f}")
```

### Custom Model Selection

```python
# Use different BERT model
engine = SemanticSearchEngine(
    model_name="sentence-transformers/msmarco-MiniLM-L-6-v3"
)
engine.initialize()

results = engine.search("your query", top_k=10)
```

### Using Embeddings Directly

```python
from embeddings import EmbeddingGenerator

generator = EmbeddingGenerator()

# Single text
embedding = generator.generate_embeddings("Hello world")
print(f"Shape: {embedding.shape}")  # (1, 384)

# Multiple texts
texts = ["First sentence", "Second sentence"]
embeddings = generator.generate_embeddings(texts)
print(f"Shape: {embeddings.shape}")  # (2, 384)

# Save embeddings
generator.save_embeddings(embeddings, "my_embeddings.npy")

# Load embeddings
loaded = generator.load_embeddings("my_embeddings.npy")
```

### Working with FAISS Index

```python
from vector_database import FAISSIndex, build_faiss_index
import numpy as np

# Create sample embeddings
embeddings = np.random.rand(1000, 384).astype(np.float32)

# Build index
faiss_idx = build_faiss_index(
    embeddings=embeddings,
    index_type="IndexFlatL2",
    metric="cosine"
)

# Search
query = embeddings[0]  # Use first embedding as query
distances, indices = faiss_idx.search(query, top_k=5)

print(f"Found {len(indices[0])} results")
print(f"Distances: {distances[0]}")
print(f"Indices: {indices[0]}")

# Save index
faiss_idx.save("my_index.index")

# Load index
new_idx = FAISSIndex(embedding_dim=384)
new_idx.load("my_index.index")
```

### Evaluation Metrics

```python
from search_engine.ranking import (
    calculate_recall_at_k,
    calculate_precision_at_k,
    calculate_mean_reciprocal_rank,
    evaluate_search_quality
)

# Example evaluation
relevant_docs = {1, 5, 10, 15}  # Ground truth relevant document IDs
retrieved_docs = [1, 3, 5, 8, 10, 12, 15, 18, 20, 25]  # Retrieved IDs

recall_5 = calculate_recall_at_k(relevant_docs, retrieved_docs, k=5)
precision_5 = calculate_precision_at_k(relevant_docs, retrieved_docs, k=5)
mrr = calculate_mean_reciprocal_rank(relevant_docs, retrieved_docs)

print(f"Recall@5: {recall_5:.4f}")
print(f"Precision@5: {precision_5:.4f}")
print(f"MRR: {mrr:.4f}")

# Full evaluation
metrics = evaluate_search_quality(results, relevant_docs)
for metric, value in metrics.items():
    print(f"{metric}: {value:.4f}")
```

### Visualization

```python
from utils.visualization import SearchVisualizer
import matplotlib.pyplot as plt
import numpy as np

visualizer = SearchVisualizer()

# Plot similarity distribution
scores = [0.85, 0.82, 0.78, 0.75, 0.72, 0.68, 0.65, 0.62, 0.58, 0.55]
fig = visualizer.plot_similarity_distribution(scores)
plt.show()

# Plot t-SNE visualization
from utils.config import EMBEDDINGS_CACHE_FILE
embeddings = np.load(EMBEDDINGS_CACHE_FILE)
sample_indices = np.random.choice(len(embeddings), 500, replace=False)
fig = visualizer.plot_embedding_tsne(embeddings[sample_indices])
plt.show()

# Plot search quality
results = [
    {'similarity_score': s, 'document_id': i}
    for i, s in enumerate(scores)
]
fig = visualizer.plot_search_results_quality(results)
plt.show()
```

---

## 🌐 REST API Usage

### Test with cURL

#### Single Search

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning applications",
    "top_k": 10,
    "threshold": 0.5
  }'
```

#### Batch Search

```bash
curl -X POST "http://localhost:8000/search/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "deep learning",
      "neural networks",
      "data science"
    ],
    "top_k": 5
  }'
```

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Get Statistics

```bash
curl http://localhost:8000/stats
```

### Using Python Requests

```python
import requests

# Single search
response = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "natural language processing",
        "top_k": 10,
        "threshold": 0.5
    }
)

results = response.json()
print(f"Found {results['n_results']} results")
print(f"Processing time: {results['processing_time_ms']:.2f}ms")

for result in results['top_results']:
    print(f"{result['rank']}. Score: {result['similarity_score']:.3f}")
    print(f"   Text: {result['text'][:100]}...")

# Batch search
response = requests.post(
    "http://localhost:8000/search/batch",
    json={
        "queries": ["query1", "query2"],
        "top_k": 5
    }
)

batch_results = response.json()
```

### Using JavaScript Fetch

```javascript
// Single search
fetch('http://localhost:8000/search', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        query: 'machine learning',
        top_k: 10,
        threshold: 0.5
    })
})
.then(response => response.json())
.then(data => {
    console.log('Results:', data);
    data.top_results.forEach(result => {
        console.log(`#${result.rank}: ${result.similarity_score}`);
    });
});

// Batch search
fetch('http://localhost:8000/search/batch', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        queries: ['query1', 'query2'],
        top_k: 5
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

### Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all available endpoints
- Test API calls directly from browser
- See request/response schemas
- Download OpenAPI specification

---

## 🖥️ Web Interface Usage

### Starting the Web UI

```bash
streamlit run web_app/app.py --server.port 8501
```

Access at: http://localhost:8501

### Features

1. **Search Box**: Enter your query
2. **Sidebar Controls**:
   - Number of results (1-20)
   - Similarity threshold (0.0-1.0)
   - System statistics display
3. **Results Display**:
   - Ranked results with scores
   - Processing time metrics
   - Average similarity score
4. **Example Queries**: Click predefined queries to test

### Customization

Edit `web_app/app.py` to customize:
- Color scheme (CSS variables)
- Default parameters
- Layout and styling
- Additional features

---

## ⚙️ Advanced Configuration

### Configuration File

Edit `utils/config.py` to customize:

```python
# Model selection
BERT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# Alternatives:
# - "sentence-transformers/msmarco-MiniLM-L-6-v3" (better for search)
# - "sentence-transformers/all-mpnet-base-v2" (higher quality)

# Embedding parameters
EMBEDDING_DIMENSION = 384
MAX_SEQ_LENGTH = 256
BATCH_SIZE = 32  # Increase for GPU, decrease for memory issues

# FAISS configuration
FAISS_INDEX_TYPE = "IndexFlatL2"  # or "IndexIVFFlat"
FAISS_NPROBE = 5  # For IVF index
FAISS_METRIC = "cosine"  # or "L2"

# Search configuration
TOP_K_RESULTS = 10
SIMILARITY_THRESHOLD = 0.5

# Device configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
```

### Preprocessing Options

```python
from preprocessing import TextCleaner

cleaner = TextCleaner(
    lowercase=True,           # Convert to lowercase
    remove_punctuation=True,  # Remove punctuation
    remove_stopwords=True,    # Remove common words
    remove_special_chars=True,# Remove URLs, mentions, etc.
    remove_numbers=True,      # Remove digits
    min_length=10             # Minimum text length
)

# Customize for your use case
cleaner_custom = TextCleaner(
    lowercase=True,
    remove_punctuation=False,  # Keep punctuation for code search
    remove_stopwords=False,    # Keep stopwords for legal documents
    min_length=5               # Shorter minimum length
)
```

---

## 🎨 Customization Examples

### Domain-Specific Search

```python
# For scientific papers
engine = SemanticSearchEngine(
    model_name="sentence-transformers/scibert_scivocab_uncased"
)

# For legal documents
engine = SemanticSearchEngine(
    model_name="sentence-transformers/legal-bert-base"
)

# For multilingual search
engine = SemanticSearchEngine(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

### Hybrid Search (BM25 + BERT)

```python
from rank_bm25 import BM25Okapi

# Prepare BM25 index
tokenized_docs = [doc.split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)

# BM25 search
query_tokens = query.split()
bm25_scores = bm25.get_scores(query_tokens)

# Combine with BERT scores
final_scores = 0.7 * bert_scores + 0.3 * bm25_scores
```

### Query Expansion

```python
def expand_query(query, synonyms_dict):
    """Expand query with synonyms."""
    words = query.split()
    expanded = []
    
    for word in words:
        if word in synonyms_dict:
            expanded.extend([word, synonyms_dict[word]])
        else:
            expanded.append(word)
    
    return ' '.join(expanded)

synonyms = {
    "ml": "machine learning",
    "nn": "neural network",
    "dl": "deep learning"
}

expanded_query = expand_query("ml algorithms", synonyms)
results = engine.search(expanded_query)
```

---

## 🚀 Performance Tuning

### For Large Datasets (>100k documents)

```python
# Use IVF index instead of flat index
faiss_index = build_faiss_index(
    embeddings=embeddings,
    index_type="IndexIVFFlat",
    metric="cosine"
)

# Tune nprobe (higher = more accurate but slower)
faiss_index.nprobe = 10  # Default: 5

# Adjust n_clusters based on dataset size
n_clusters = int(np.sqrt(len(embeddings)))  # Rule of thumb
```

### GPU Acceleration

```bash
# Install GPU version of FAISS
pip uninstall faiss-cpu
pip install faiss-gpu

# Update config.py
DEVICE = "cuda"
BATCH_SIZE = 64  # Increase batch size
```

### Memory Optimization

```python
# Reduce batch size
BATCH_SIZE = 16

# Use smaller model
BERT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Clear CUDA cache (if using GPU)
import torch
torch.cuda.empty_cache()
```

### Caching Strategy

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_search(query: str, top_k: int):
    return engine.search(query, top_k=top_k)

# Frequently used queries will be cached
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: "CUDA out of memory"

**Solution:**
```python
# Reduce batch size
BATCH_SIZE = 8  # or 16

# Or use CPU
DEVICE = "cpu"
```

#### Issue: Slow search performance

**Solutions:**
1. Use IVF index
2. Reduce top_k value
3. Enable GPU acceleration
4. Decrease nprobe (for IVF)

#### Issue: Poor search quality

**Solutions:**
1. Try different model
2. Lower similarity threshold
3. Improve text preprocessing
4. Add more training data

#### Issue: Model download fails

**Solution:**
```python
# Manually download model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer(
    'all-MiniLM-L6-v2',
    cache_folder='/path/to/cache'
)
```

#### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Ensure you're in project directory
cd semantic-search-engine
```

---

## 📊 Monitoring and Logging

### View Logs

```bash
# Real-time log viewing
tail -f logs/semantic_search.log

# Or on Windows
Get-Content logs/semantic_search.log -Wait
```

### Log Levels

Edit `utils/config.py`:

```python
LOG_LEVEL = "DEBUG"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

## 🎓 Best Practices

### 1. Data Quality
- Clean your data thoroughly
- Remove duplicates
- Ensure consistent formatting
- Handle missing values

### 2. Model Selection
- Start with `all-MiniLM-L6-v2` (fast)
- Upgrade to `msmarco-MiniLM-L-6-v3` for better quality
- Use domain-specific models when available

### 3. Index Configuration
- Use IndexFlatL2 for <100k documents
- Use IndexIVFFlat for larger datasets
- Tune nprobe based on accuracy/speed tradeoff

### 4. Production Deployment
- Use Docker for consistency
- Implement health checks
- Set up monitoring
- Cache frequent queries
- Use load balancing for high traffic

---

## 📚 Additional Resources

- **Full Documentation**: README.md
- **Quick Start**: QUICKSTART.md
- **Examples**: notebooks/exploration.ipynb
- **API Docs**: http://localhost:8000/docs
- **Tests**: tests/test_search.py

---

**Happy Searching! 🔍**

For questions or support, refer to the main README.md or open an issue on GitHub.
