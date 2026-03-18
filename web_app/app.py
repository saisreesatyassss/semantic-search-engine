"""
Streamlit web application for Semantic Search Engine - Dark Mode Only
Clean interface with white search bar and minimal options
"""
import streamlit as st
import time
from typing import List, Dict
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Semantic Search Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling (light theme)
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .search-box {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 4px solid #1E88E5;
    }
    .score-badge {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .rank-badge {
        display: inline-block;
        background-color: #FF9800;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin-right: 10px;
    }
    .stats-container {
        background-color: #E3F2FD;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


def initialize_search_engine():
    """Initialize search engine with caching."""
    from search_engine.semantic_search import SemanticSearchEngine
    
    @st.cache_resource
    def get_engine():
        engine = SemanticSearchEngine()
        engine.initialize()
        return engine
    
    return get_engine()


def render_result_card(result: Dict, rank: int):
    """Render a single result card."""
    score = result.get('similarity_score', 0)
    score_pct = score * 100 if score <= 1 else score
    
    with st.container():
        st.markdown(f"""
        <div class="result-card">
            <span class="rank-badge">#{rank}</span>
            <span class="score-badge">Score: {score_pct:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
        
        if result.get('title'):
            st.markdown(f"**{result['title']}**")
        
        st.caption(f"Document ID: {result.get('document_id', 'N/A')}")
        
        text = result.get('text', '')
        if len(text) > 500:
            text = text[:500] + "..."
        
        st.write(text)
        st.divider()


def main():
    """Main application function."""
    
    # Initialize search engine
    with st.spinner("Initializing search engine..."):
        try:
            search_engine = initialize_search_engine()
            stats = search_engine.get_statistics()
        except Exception as e:
            st.error(f"Failed to initialize search engine: {e}")
            st.stop()
    
    # Header without icons
    st.markdown('<h1 class="main-header">Semantic Search Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Powered by BERT and FAISS | Intelligent Document Retrieval</p>', unsafe_allow_html=True)
    
    # Sidebar with statistics
    with st.sidebar:
        st.header("System Statistics")
        
        st.markdown(f"""
        <div class="stats-container">
            <p><strong>Model:</strong> {stats.get('model_name', 'Unknown')}</p>
            <p><strong>Documents:</strong> {stats.get('n_documents', 0):,}</p>
            <p><strong>Embedding Dim:</strong> {stats.get('embedding_dimension', 0)}</p>
            <p><strong>Index Type:</strong> {stats.get('index_type', 'Unknown')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Settings
        st.subheader("Search Settings")
        top_k = st.slider("Number of Results", min_value=1, max_value=20, value=10)
        threshold = st.slider("Similarity Threshold", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
        
        st.divider()
        
        # Info
        st.info("""
        How it works:
        1. Enter your search query
        2. The system converts your query to a semantic embedding
        3. FAISS searches for similar document embeddings
        4. Results are ranked by similarity score
        """)
    
    # Main search area - White search bar
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="Enter your search query (e.g., 'deep learning for medical imaging')",
            label_visibility="collapsed"
        )
    
    with col2:
        search_button = st.button("Search", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Session state for results
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'processing_time' not in st.session_state:
        st.session_state.processing_time = 0
    
    # Handle search
    if search_button and query:
        with st.spinner(f"Searching for '{query}'..."):
            start_time = time.time()
            
            try:
                results = search_engine.search(
                    query=query,
                    top_k=top_k,
                    threshold=threshold
                )
                
                processing_time = time.time() - start_time
                
                st.session_state.results = results
                st.session_state.processing_time = processing_time
                
            except Exception as e:
                st.error(f"Search failed: {e}")
                st.session_state.results = []
    
    # Display results
    if st.session_state.results:
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Results Found",
                value=len(st.session_state.results),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Processing Time",
                value=f"{st.session_state.processing_time*1000:.1f}ms",
                delta=None
            )
        
        with col3:
            avg_score = np.mean([r['similarity_score'] for r in st.session_state.results])
            st.metric(
                label="Avg Similarity",
                value=f"{avg_score*100:.1f}%",
                delta=None
            )
        
        st.divider()
        
        st.subheader("Search Results")
        
        # Display each result
        for i, result in enumerate(st.session_state.results, 1):
            render_result_card(result, i)
    
    # Example queries
    if not st.session_state.results:
        st.divider()
        
        st.subheader("Example Queries")
        
        example_queries = [
            "machine learning algorithms for classification",
            "neural networks and deep learning",
            "data preprocessing techniques",
            "natural language processing applications"
        ]
        
        cols = st.columns(len(example_queries))
        
        for i, example in enumerate(example_queries):
            with cols[i]:
                if st.button(example, key=f"example_{i}", use_container_width=True):
                    st.session_state.query = example
                    st.rerun()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>Built with Sentence-BERT, FAISS, FastAPI, and Streamlit</p>
        <p>Semantic Search Engine v1.0.0</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
