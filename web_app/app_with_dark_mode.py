"""
Streamlit web application for Semantic Search Engine with Dark Mode
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
    initial_sidebar_state="expanded"
)

# Initialize session state for theme
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True  # Default to dark mode

# Theme toggle function
def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Get current theme
dark_mode = st.session_state.dark_mode

# Color schemes based on theme
if dark_mode:
    bg_color = "#1a1a2e"
    card_bg = "#16213e"
    text_color = "#ffffff"
    secondary_text = "#b0b0b0"
    border_color = "#0f3460"
    search_bg = "#0f3460"
    stats_bg = "#16213e"
    hover_bg = "#1f4287"
else:
    bg_color = "#f8f9fa"
    card_bg = "#ffffff"
    text_color = "#333333"
    secondary_text = "#666666"
    border_color = "#e0e0e0"
    search_bg = "#f5f5f5"
    stats_bg = "#e3f2fd"
    hover_bg = "#e8f4fc"

# Custom CSS with theme support
st.markdown(f"""
<style>
    /* Theme Variables */
    :root {{
        --bg-color: {bg_color};
        --card-bg: {card_bg};
        --text-color: {text_color};
        --secondary-text: {secondary_text};
        --border-color: {border_color};
        --search-bg: {search_bg};
        --stats-bg: {stats_bg};
        --hover-bg: {hover_bg};
        --primary-color: #1E88E5;
        --score-color: #4CAF50;
        --rank-color: #FF9800;
    }}
    
    /* Main container background */
    .stApp {{
        background-color: var(--bg-color);
        transition: all 0.3s ease;
    }}
    
    /* Header Styling */
    .main-header {{
        font-size: 3rem;
        font-weight: bold;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 1rem;
        transition: color 0.3s ease;
    }}
    
    .sub-header {{
        font-size: 1.2rem;
        color: var(--secondary-text);
        text-align: center;
        margin-bottom: 2rem;
        transition: color 0.3s ease;
    }}
    
    /* Search Box */
    .search-box {{
        background-color: var(--search-bg);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }}
    
    /* Result Cards */
    .result-card {{
        background-color: var(--card-bg);
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        margin-bottom: 15px;
        border-left: 4px solid var(--primary-color);
        transition: all 0.3s ease;
    }}
    
    .result-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        background-color: var(--hover-bg);
    }}
    
    /* Score Badge */
    .score-badge {{
        display: inline-block;
        background-color: var(--score-color);
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin-bottom: 10px;
    }}
    
    /* Rank Badge */
    .rank-badge {{
        display: inline-block;
        background-color: var(--rank-color);
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin-right: 10px;
    }}
    
    /* Stats Container */
    .stats-container {{
        background-color: var(--stats-bg);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }}
    
    /* Text colors */
    .stMarkdown, .st-ae, .block-container {{
        color: var(--text-color) !important;
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg-color);
    }}
    
    section[data-testid="stSidebar"] * {{
        color: var(--text-color) !important;
    }}
    
    /* Input fields */
    .stTextInput > div > div > input {{
        background-color: var(--search-bg);
        color: var(--text-color);
        border: 1px solid var(--border-color);
    }}
    
    /* Metric cards */
    [data-testid="stMetric"] {{
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 10px;
    }}
    
    [data-testid="stMetricValue"] {{
        color: var(--text-color) !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: var(--secondary-text) !important;
    }}
    
    /* Divider styling */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 20px 0;
    }}
    
    /* Button styling */
    .stButton > button {{
        transition: all 0.3s ease;
    }}
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
    
    # Format score as percentage
    score_pct = score * 100 if score <= 1 else score
    
    with st.container():
        st.markdown(f"""
        <div class="result-card">
            <span class="rank-badge">#{rank}</span>
            <span class="score-badge">Score: {score_pct:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Display title if available
        if result.get('title'):
            st.markdown(f"**{result['title']}")
        
        # Display document ID
        st.caption(f"Document ID: {result.get('document_id', 'N/A')}")
        
        # Display text (truncated if too long)
        text = result.get('text', '')
        if len(text) > 500:
            text = text[:500] + "..."
        
        st.write(text)
        
        st.divider()


def main():
    """Main application function."""
    
    # Theme toggle in sidebar - Top section
    with st.sidebar:
        st.subheader("🎨 Appearance")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙 Dark", 
                        key="dark_btn", 
                        use_container_width=True,
                        disabled=dark_mode):
                st.session_state.dark_mode = True
                st.rerun()
        
        with col2:
            if st.button("☀️ Light", 
                        key="light_btn", 
                        use_container_width=True,
                        disabled=not dark_mode):
                st.session_state.dark_mode = False
                st.rerun()
        
        st.divider()
        
        st.subheader("⚙️ Search Settings")
        top_k = st.slider("Number of Results", min_value=1, max_value=20, value=10)
        threshold = st.slider("Similarity Threshold", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
        
        st.divider()
        
        # Info
        st.info("""
        **How it works:**
        1. Enter your search query
        2. The System converts your query to a semantic embedding
        3. FAISS searches for similar document embeddings
        4. Results are ranked by similarity score
        """)
    
    # Header
    st.markdown('<h1 class="main-header">🔍 Semantic Search Engine</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Powered by BERT and FAISS | Intelligent Document Retrieval</p>', unsafe_allow_html=True)
    
    # Initialize search engine
    with st.spinner("Initializing search engine..."):
        try:
            search_engine = initialize_search_engine()
            stats = search_engine.get_statistics()
        except Exception as e:
            st.error(f"Failed to initialize search engine: {e}")
            st.stop()
    
    # Continue sidebar with statistics
    with st.sidebar:
        st.header("📊 System Statistics")
        
        st.markdown(f"""
        <div class="stats-container">
            <p style="color: {text_color};"><strong>Model:</strong> {stats.get('model_name', 'Unknown')}</p>
            <p style="color: {text_color};"><strong>Documents:</strong> {stats.get('n_documents', 0):,}</p>
            <p style="color: {text_color};"><strong>Embedding Dim:</strong> {stats.get('embedding_dimension', 0)}</p>
            <p style="color: {text_color};"><strong>Index Type:</strong> {stats.get('index_type', 'Unknown')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main search area
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="Enter your search query (e.g., 'deep learning for medical imaging')",
            label_visibility="collapsed"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
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
        
        st.subheader("📄 Search Results")
        
        # Display each result
        for i, result in enumerate(st.session_state.results, 1):
            render_result_card(result, i)
    
    # Example queries
    if not st.session_state.results:
        st.divider()
        
        st.subheader("💡 Example Queries")
        
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
    st.markdown(f"""
    <div style="text-align: center; color: {secondary_text}; padding: 20px; margin-top: 30px; border-top: 1px solid {border_color};">
        <p>Built with ❤️ using Sentence-BERT, FAISS, FastAPI, and Streamlit</p>
        <p>Semantic Search Engine v1.0.0</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
