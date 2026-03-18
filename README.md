# 🔍 Semantic Search Engine using BERT and FAISS

A production-ready semantic search system that understands the meaning of text queries using transformer embeddings instead of keyword matching.

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit Deploy](https://img.shields.io/badge/streamlit-ready-FF4B4B?logo=streamlit)

---

## 🚀 Streamlit Cloud Deployment Ready

This project is **fully configured and optimized** for deployment on Streamlit Community Cloud!

### Quick Deploy
```bash
# Run automated deployment script
deploy.bat

# Or manually:
python test_deployment.py
git add .
git commit -m "Ready for Streamlit Cloud"
git push origin main
```

Then deploy at [share.streamlit.io](https://share.streamlit.io) with:
- **Main file**: `app.py`
- **Branch**: `main`

📖 **See**: [`STREAMLIT_READY.md`](STREAMLIT_READY.md) for complete deployment guide

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Performance Optimization](#performance-optimization)
- [Deployment](#deployment)
- [Evaluation](#evaluation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This Semantic Search Engine leverages state-of-the-art **Sentence-BERT** for generating high-quality text embeddings and **FAISS** (Facebook AI Similarity Search) for fast, efficient similarity search. Unlike traditional keyword-based search systems, this engine understands semantic meaning, enabling it to find relevant documents even when they don't share exact words with the query.

### Key Capabilities

- ✅ **Semantic Understanding**: Finds documents by meaning, not just keywords
- ✅ **Fast Search**: Sub-second search through thousands of documents using FAISS
- ✅ **Production-Ready**: RESTful API with FastAPI and interactive web UI with Streamlit
- ✅ **Scalable Architecture**: Modular design supporting both CPU and GPU deployment
- ✅ **Evaluation Metrics**: Built-in precision, recall, and MRR calculations

---

## 🏗️ Architecture

```
┌─────────────────┐
│  User Query     │
│  "deep learning │
│   for medical   │
│   imaging"      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Text Preprocessing Pipeline       │
│   - Lowercase                       │
│   - Remove stopwords                │
│   - Normalize text                  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Sentence-BERT Embedding Model     │
│   (all-MiniLM-L6-v2)                │
│   Output: 384-dim vector            │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   FAISS Vector Index                │
│   - IndexFlatL2 / IndexIVFFlat      │
│   - Cosine Similarity Search        │
│   - O(1) retrieval time             │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Ranked Results                    │
│   - Document 1: Score 0.89          │
│   - Document 2: Score 0.85          │
│   - Document 3: Score 0.78          │
└─────────────────────────────────────┘
```

---

## ✨ Features

### Core Features
- **Semantic Search**: Understands query intent and context
- **Fast Retrieval**: FAISS-powered similarity search in milliseconds
- **Pre-trained Models**: Ready-to-use Sentence-BERT embeddings
- **Batch Processing**: Handle multiple queries efficiently
- **Similarity Scoring**: Cosine similarity scores for all results

### Advanced Features
- **Multiple Index Types**: Support for both exact (IndexFlatL2) and approximate (IndexIVFFlat) search
- **Configurable Thresholds**: Filter results by minimum similarity score
- **Document Metadata**: Store and retrieve additional document information
- **Evaluation Metrics**: Precision@K, Recall@K, MRR calculations
- **Visualization Tools**: t-SNE plots, similarity distributions

### Production Features
- **RESTful API**: FastAPI backend with automatic OpenAPI documentation
- **Interactive UI**: Streamlit web interface for non-technical users
- **Docker Support**: Containerized deployment with docker-compose
- **Health Checks**: Built-in monitoring and status endpoints
- **Logging**: Comprehensive logging for debugging and monitoring

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git (for cloning the repository)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd semantic-search-engine
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download NLTK Data

The first run will automatically download required NLTK data. Alternatively:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

---

## ⚡ Quick Start

### 1. Download and Prepare Dataset

```bash
python scripts/download_data.py
```

This will:
- Download StackOverflow questions dataset
- Clean and preprocess text
- Save processed data to `data/processed/`

### 2. Build Embeddings and FAISS Index

```bash
python scripts/build_index.py
```

This will:
- Generate BERT embeddings for all documents
- Create FAISS vector index
- Save index and metadata

### 3. Start FastAPI Server

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### 4. Launch Streamlit Web Interface

```bash
streamlit run web_app/app.py --server.port 8501
```

Web UI will be available at: `http://localhost:8501`

---

## 📖 Usage Guide

### Python API Usage

```python
from search_engine import SemanticSearchEngine

# Initialize engine
engine = SemanticSearchEngine()
engine.initialize()

# Single search
results = engine.search(
    query="neural networks for image classification",
    top_k=10,
    threshold=0.5
)

for result in results:
    print(f"Rank {result['rank']}: Score {result['similarity_score']:.3f}")
    print(f"Text: {result['text'][:200]}...")
    print("-" * 80)

# Batch search
queries = [
    "machine learning algorithms",
    "deep learning frameworks"
]
all_results = engine.search_batch(queries, top_k=5)
```

### REST API Usage

#### Single Search

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "deep learning for medical imaging",
    "top_k": 10,
    "threshold": 0.5
  }'
```

#### Batch Search

```bash
curl -X POST "http://localhost:8000/search/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": ["machine learning", "neural networks"],
    "top_k": 5
  }'
```

#### Health Check

```bash
curl http://localhost:8000/health
```

### Using the Web Interface

1. Navigate to `http://localhost:8501`
2. Enter your search query in the search box
3. Adjust parameters (number of results, threshold) in sidebar
4. Click "🔍 Search" button
5. View ranked results with similarity scores
6. Try example queries from the bottom section

---

## 📡 API Documentation

### Endpoints

#### `POST /search`

Search for semantically similar documents.

**Request Body:**
```json
{
  "query": "your search query",
  "top_k": 10,
  "threshold": 0.5
}
```

**Response:**
```json
{
  "query": "your search query",
  "top_results": [
    {
      "rank": 1,
      "document_id": 123,
      "text": "Document content...",
      "title": "Document title",
      "similarity_score": 0.89,
      "metadata": {}
    }
  ],
  "n_results": 10,
  "processing_time_ms": 45.2
}
```

#### `POST /search/batch`

Search for multiple queries simultaneously.

#### `GET /health`

Get service health status and statistics.

#### `GET /stats`

Get detailed system statistics.

---

## 📁 Project Structure

```
semantic-search-engine/
├── data/
│   ├── raw/                      # Raw downloaded datasets
│   └── processed/                # Cleaned and preprocessed data
├── preprocessing/
│   ├── text_cleaner.py           # Text normalization functions
│   └── data_loader.py            # Dataset loading utilities
├── embeddings/
│   ├── embedding_generator.py    # BERT embedding creation
│   └── model_loader.py           # Model loading configuration
├── vector_database/
│   ├── faiss_index.py            # FAISS index management
│   └── index_utils.py            # Index utilities
├── search_engine/
│   ├── semantic_search.py        # Core search functionality
│   └── ranking.py                # Result ranking and scoring
├── api/
│   ├── main.py                   # FastAPI application
│   └── schemas.py                # Pydantic models
├── web_app/
│   └── app.py                    # Streamlit interface
├── utils/
│   ├── config.py                 # Configuration constants
│   ├── logger.py                 # Logging setup
│   └── visualization.py          # Plotting utilities
├── scripts/
│   ├── download_data.py          # Data preparation script
│   └── build_index.py            # Index building script
├── models/saved_models/          # Stored trained models
├── notebooks/                     # Jupyter notebooks for analysis
├── tests/                         # Unit and integration tests
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker container config
├── docker-compose.yml             # Multi-service orchestration
└── README.md                      # This file
```

---

## ⚙️ Performance Optimization

### 1. Model Selection

Choose based on your needs:

```python
# Fast inference (recommended for most use cases)
model_name = "sentence-transformers/all-MiniLM-L6-v2"

# Better search quality (slower)
model_name = "sentence-transformers/msmarco-MiniLM-L-6-v3"

# Highest quality (slowest)
model_name = "sentence-transformers/all-mpnet-base-v2"
```

### 2. FAISS Index Type

```python
# For small datasets (<100k documents)
index_type = "IndexFlatL2"  # Exact search

# For large datasets (>100k documents)
index_type = "IndexIVFFlat"  # Approximate search, faster
n_clusters = 100  # Adjust based on dataset size
nprobe = 5  # Number of clusters to search
```

### 3. Batch Processing

```python
# Increase batch size for GPU
batch_size = 64  # Default: 32

# Process multiple queries together
results = engine.search_batch(queries, top_k=10)
```

### 4. GPU Acceleration

Install GPU version of FAISS:

```bash
pip uninstall faiss-cpu
pip install faiss-gpu
```

Update `utils/config.py`:

```python
DEVICE = "cuda"  # Instead of "cpu"
```

---

## 🐳 Deployment

### Docker Deployment

#### Build and Run with Docker Compose

```bash
docker-compose up --build
```

This starts both API and UI services:
- API: `http://localhost:8000`
- UI: `http://localhost:8501`

#### Run Individual Services

```bash
# Build Docker image
docker build -t semantic-search .

# Run API container
docker run -p 8000:8000 -v $(pwd)/data:/app/data semantic-search \
  python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Run UI container
docker run -p 8501:8501 -v $(pwd)/data:/app/data semantic-search \
  python -m streamlit run web_app/app.py
```

### Production Considerations

1. **Environment Variables**: Configure via `.env` file
2. **Reverse Proxy**: Use Nginx or Traefik
3. **Load Balancing**: Multiple API instances
4. **Caching**: Redis for frequent queries
5. **Monitoring**: Prometheus + Grafana
6. **Logging**: ELK stack or CloudWatch

---

## 📊 Evaluation

### Evaluate Search Quality

```python
from search_engine.ranking import evaluate_search_quality

# Define ground truth
relevant_docs = {1, 5, 10, 15, 20}

# Get search results
results = engine.search("machine learning", top_k=10)
retrieved_ids = [r['document_id'] for r in results]

# Calculate metrics
metrics = evaluate_search_quality(results, relevant_docs)

print(f"Recall@5: {metrics['recall@5']:.3f}")
print(f"Precision@10: {metrics['precision@10']:.3f}")
print(f"MRR: {metrics['mrr']:.3f}")
```

### Visualization

```python
from utils.visualization import SearchVisualizer

visualizer = SearchVisualizer()

# Plot similarity distribution
scores = [r['similarity_score'] for r in results]
fig = visualizer.plot_similarity_distribution(scores)
plt.show()

# Plot embeddings in 2D
from utils.config import EMBEDDINGS_CACHE_FILE
embeddings = np.load(EMBEDDINGS_CACHE_FILE)
fig = visualizer.plot_embedding_tsne(embeddings[:1000])
plt.show()
```

---

## 🔧 Troubleshooting

### Issue: Out of Memory Error

**Solution**: Reduce batch size or use smaller model
```python
batch_size = 16  # Reduce from 32
model_name = "sentence-transformers/all-MiniLM-L6-v2"
```

### Issue: Slow Search Performance

**Solutions**:
1. Use IndexIVFFlat instead of IndexFlatL2
2. Reduce nprobe value
3. Enable GPU acceleration
4. Decrease top_k value

### Issue: Poor Search Quality

**Solutions**:
1. Try different BERT model (msmarco-MiniLM-L-6-v3)
2. Lower similarity threshold
3. Improve text preprocessing
4. Increase dataset size

### Issue: Model Download Fails

**Solution**: Manual download
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/path/to/cache')
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Add type hints to functions
- Include docstrings for classes and methods
- Write unit tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Sentence Transformers**: https://github.com/UKPLab/sentence-transformers
- **FAISS**: https://github.com/facebookresearch/faiss
- **FastAPI**: https://fastapi.tiangolo.com
- **Streamlit**: https://streamlit.io

---

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Email: your-email@example.com
- Documentation: https://your-docs-url.com

---

## 🎓 Citation

If you use this project in your research, please cite:

```bibtex
@software{semantic_search_engine2024,
  title = {Semantic Search Engine using BERT and FAISS},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/semantic-search-engine}
}
```

---

**Built with ❤️ using Sentence-BERT, FAISS, FastAPI, and Streamlit**
