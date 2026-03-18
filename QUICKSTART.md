# Quick Start Guide

## Semantic Search Engine using BERT and FAISS

This guide will help you get the semantic search engine up and running in under 10 minutes.

---

## 🚀 Installation (5 minutes)

### Step 1: Create Virtual Environment

```bash
# Navigate to project directory
cd semantic-search-engine

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📊 Build Search Index (3 minutes)

### Step 1: Download Dataset

```bash
python scripts/download_data.py
```

This downloads StackOverflow questions and preprocesses them.

### Step 2: Generate Embeddings and Build Index

```bash
python scripts/build_index.py
```

This creates BERT embeddings and builds the FAISS index.

**Expected Output:**
- `data/processed/embeddings.npy` - Document embeddings
- `vector_database/faiss.index` - FAISS index file
- `data/processed/metadata.pkl` - Document metadata

---

## 🔍 Run the Application (1 minute)

### Option 1: FastAPI Backend Only

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Access:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Test with curl:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 5}'
```

### Option 2: Streamlit Web Interface

```bash
streamlit run web_app/app.py --server.port 8501
```

**Access:**
- Web UI: http://localhost:8501

### Option 3: Both API and UI

Open two terminal windows:

**Terminal 1:**
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2:**
```bash
streamlit run web_app/app.py --server.port 8501
```

---

## 🧪 Test the System

### Example Queries to Try

1. **Machine Learning**: "neural networks for image classification"
2. **Web Development**: "frontend frameworks for building websites"
3. **Data Science**: "statistical analysis and data visualization"
4. **Deep Learning**: "convolutional neural networks architecture"
5. **NLP**: "natural language processing text analysis"

### Python Testing

```python
from search_engine import SemanticSearchEngine

# Initialize
engine = SemanticSearchEngine()
engine.initialize()

# Search
results = engine.search(
    query="deep learning applications",
    top_k=5,
    threshold=0.5
)

# Display results
for result in results:
    print(f"\nRank {result['rank']}: Score = {result['similarity_score']:.3f}")
    print(f"Text: {result['text'][:150]}...")
```

---

## 🐳 Docker Deployment (Alternative)

If you prefer Docker:

```bash
# Build and run all services
docker-compose up --build

# Access services:
# - API: http://localhost:8000
# - UI: http://localhost:8501
```

---

## ⚡ Performance Tips

### For Faster Search

1. **Use GPU acceleration:**
   ```bash
   pip install faiss-gpu
   ```

2. **Reduce top_k value:**
   ```python
   results = engine.search(query, top_k=5)  # Instead of default 10
   ```

3. **Use IVF index for large datasets:**
   ```python
   # In build_index.py script
   index_type = "IndexIVFFlat"
   ```

### For Better Quality

1. **Use better model:**
   ```python
   # In utils/config.py
   BERT_MODEL_NAME = "sentence-transformers/msmarco-MiniLM-L-6-v3"
   ```

2. **Lower similarity threshold:**
   ```python
   results = engine.search(query, threshold=0.3)
   ```

---

## 🛠️ Troubleshooting

### Issue: "Module not found"

**Solution:** Ensure you're in the virtual environment and in the `semantic-search-engine` directory.

```bash
# Check virtual environment
which python  # Linux/Mac
where python  # Windows

# Should point to venv path
```

### Issue: "Model download failed"

**Solution:** The model will cache on first download. If it fails:

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### Issue: "Out of memory"

**Solution:** Reduce batch size in `utils/config.py`:

```python
BATCH_SIZE = 16  # Instead of 32
```

### Issue: Slow performance on Windows

**Solution:** Use WSL2 (Windows Subsystem for Linux) for better performance.

---

## 📝 Next Steps

1. **Explore the codebase**: Check out individual modules in `preprocessing/`, `embeddings/`, etc.

2. **Run the notebook**: Open `notebooks/exploration.ipynb` for interactive exploration

3. **Customize**: Modify configuration in `utils/config.py`

4. **Deploy**: Follow deployment instructions in README.md

5. **Evaluate**: Run tests with `pytest tests/ -v`

---

## 📞 Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review example queries in the Streamlit UI
- Inspect logs in `logs/semantic_search.log`

---

**Happy Searching! 🔍**
