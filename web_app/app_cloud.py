"""
Streamlit Cloud Deployment Version
Optimized for Streamlit Community Cloud free tier
"""
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import time

# Import search components
from embeddings.embedding_generator import EmbeddingGenerator
from vector_database.faiss_index import build_faiss_index, FAISSIndex
from preprocessing.data_loader import DataLoader
from preprocessing.text_cleaner import TextCleaner
from utils.config import BERT_MODEL_NAME

# Page configuration
st.set_page_config(
    page_title="Semantic Search Engine (Cloud Demo)",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .result-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 12px;
        border-left: 4px solid #1E88E5;
    }
    .score-badge {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
    .rank-badge {
        display: inline-block;
        background-color: #FF9800;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        margin-right: 8px;
        font-size: 0.9rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 4px solid #2196F3;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_search_engine():
    """
    Load search engine with caching for Streamlit Cloud.
    Generates embeddings on first load, caches for session.
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Create sample dataset
        status_text.text("Creating sample dataset...")
        loader = DataLoader(dataset_name='stackoverflow')
        df = loader.load_stackoverflow(sample_size=1000)  # Smaller for cloud
        progress_bar.progress(20)
        
        # Step 2: Preprocess text
        status_text.text("Preprocessing text...")
        cleaner = TextCleaner(
            lowercase=True,
            remove_punctuation=True,
            remove_stopwords=True,
            min_length=10
        )
        df = cleaner.clean_dataframe(df, 'text', 'cleaned_text')
        progress_bar.progress(40)
        
        # Step 3: Generate embeddings
        status_text.text("Generating BERT embeddings (this may take 1-2 minutes)...")
        generator = EmbeddingGenerator(model_name=BERT_MODEL_NAME)
        texts = df['cleaned_text'].fillna('').tolist()
        embeddings = generator.generate_embeddings(texts, batch_size=32, show_progress=False)
        progress_bar.progress(70)
        
        # Step 4: Build FAISS index
        status_text.text("Building search index...")
        faiss_index = build_faiss_index(embeddings, metric='cosine')
        progress_bar.progress(90)
        
        # Create document mapping
        doc_mapping = {}
        for idx, row in df.iterrows():
            doc_mapping[idx] = {
                'id': idx,
                'text': row.get('cleaned_text', ''),
                'title': row.get('title', '')
            }
        
        status_text.text("✅ Ready!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        return {
            'generator': generator,
            'faiss_index': faiss_index,
            'doc_mapping': doc_mapping,
            'n_docs': len(df)
        }
        
    except Exception as e:
        st.error(f"Error loading search engine: {str(e)}")
        return None


def search(query, engine_data, top_k=10, threshold=0.5):
    """Perform semantic search"""
    if not engine_data:
        return []
    
    # Generate query embedding
    query_emb = engine_data['generator'].generate_embeddings(query, show_progress=False)
    
    # Search in FAISS index
    distances, indices = engine_data['faiss_index'].search(query_emb, top_k=top_k * 2)
    
    # Format results
    results = []
    for i in range(len(indices[0])):
        doc_id = int(indices[0][i])
        if doc_id < 0 or doc_id >= len(engine_data['doc_mapping']):
            continue
        
        score = float(distances[0][i])
        if score < threshold:
            continue
            
        doc_info = engine_data['doc_mapping'][doc_id]
        results.append({
            'rank': len(results) + 1,
            'document_id': doc_id,
            'text': doc_info.get('text', ''),
            'title': doc_info.get('title', ''),
            'similarity_score': score
        })
    
    return results[:top_k]


def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔍 Semantic Search Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Powered by BERT + FAISS | Cloud Demo Version</p>', unsafe_allow_html=True)
    
    # Info box
    st.markdown("""
    <div class="info-box">
        <strong>ℹ️ Cloud Demo:</strong> This demo uses a smaller dataset (1,000 documents) 
        optimized for Streamlit Community Cloud. The full version supports 10,000+ documents 
        with persistent storage.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize search engine
    with st.spinner("Loading search engine... Please wait (first load takes 1-2 minutes)"):
        engine_data = load_search_engine()
    
    if not engine_data:
        st.error("Failed to initialize search engine. Please refresh the page.")
        return
    
    # Sidebar with stats
    with st.sidebar:
        st.header("📊 Statistics")
        st.metric("Documents Indexed", engine_data['n_docs'])
        st.metric("Embedding Dimension", 384)
        st.metric("Model", "all-MiniLM-L6-v2")
        
        st.divider()
        
        st.subheader("⚙️ Search Settings")
        top_k = st.slider("Results", min_value=1, max_value=20, value=10)
        threshold = st.slider("Threshold", min_value=0.0, max_value=1.0, value=0.3, step=0.05)
        
        st.divider()
        
        st.info("""
        **How it works:**
        1. Your query is converted to a vector embedding
        2. FAISS finds similar document vectors
        3. Results ranked by cosine similarity
        """)
    
    # Main search area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="Try: 'machine learning algorithms'",
            label_visibility="collapsed"
        )
    
    with col2:
        search_btn = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # Session state for results
    if 'results' not in st.session_state:
        st.session_state.results = []
    
    # Handle search
    if search_btn and query:
        with st.spinner(f"Searching for '{query}'..."):
            results = search(query, engine_data, top_k=top_k, threshold=threshold)
            st.session_state.results = results
    
    # Display results
    if st.session_state.results:
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Results Found", len(st.session_state.results))
        with col2:
            avg_score = np.mean([r['similarity_score'] for r in st.session_state.results])
            st.metric("Avg Similarity", f"{avg_score:.2%}")
        
        st.divider()
        
        st.subheader("📄 Search Results")
        
        for result in st.session_state.results:
            with st.container():
                st.markdown(f"""
                <div class="result-card">
                    <span class="rank-badge">#{result['rank']}</span>
                    <span class="score-badge">Score: {result['similarity_score']:.2%}</span>
                </div>
                """, unsafe_allow_html=True)
                
                text = result['text'][:300] + "..." if len(result['text']) > 300 else result['text']
                st.write(text)
                st.divider()
    
    # Example queries
    if not st.session_state.results:
        st.divider()
        
        st.subheader("💡 Example Queries")
        
        example_queries = [
            "machine learning basics",
            "neural networks",
            "web development",
            "data science"
        ]
        
        cols = st.columns(len(example_queries))
        for i, example in enumerate(example_queries):
            with cols[i]:
                if st.button(example, key=f"ex_{i}", use_container_width=True):
                    st.session_state.query = example
                    results = search(example, engine_data, top_k=top_k, threshold=threshold)
                    st.session_state.results = results
                    st.experimental_rerun()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 10px;">
        <p>Built with Sentence-BERT + FAISS + FastAPI + Streamlit</p>
        <p><a href="https://github.com/yourusername/semantic-search-engine" target="_blank">View on GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
