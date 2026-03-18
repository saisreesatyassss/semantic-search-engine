"""
Visualization utilities for semantic search analysis
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any
from sklearn.manifold import TSNE
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SearchVisualizer:
    """
    Visualization tools for search results and embeddings.
    """
    
    def __init__(self, style: str = 'seaborn-v0_8'):
        """
        Initialize visualizer with styling.
        
        Args:
            style: Matplotlib/seaborn style to use
        """
        plt.style.use(style)
        self.colors = plt.cm.viridis(np.linspace(0.2, 0.8, 10))
        
        logger.info("SearchVisualizer initialized")
    
    def plot_similarity_distribution(
        self,
        similarity_scores: List[float],
        title: str = "Distribution of Similarity Scores"
    ) -> plt.Figure:
        """
        Plot histogram of similarity scores.
        
        Args:
            similarity_scores: List of similarity scores
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(similarity_scores, bins=20, color=self.colors[0], 
                edgecolor='black', alpha=0.7)
        ax.set_xlabel('Similarity Score', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add mean line
        mean_score = np.mean(similarity_scores)
        ax.axvline(mean_score, color='red', linestyle='--', 
                  linewidth=2, label=f'Mean: {mean_score:.3f}')
        ax.legend()
        
        plt.tight_layout()
        logger.info("Created similarity distribution plot")
        
        return fig
    
    def plot_embedding_tsne(
        self,
        embeddings: np.ndarray,
        titles: List[str] = None,
        n_samples: int = 1000,
        title: str = "t-SNE Visualization of Document Embeddings"
    ) -> plt.Figure:
        """
        Create t-SNE visualization of embeddings.
        
        Args:
            embeddings: Embedding matrix (n_docs, embedding_dim)
            titles: Optional document titles for tooltips
            n_samples: Number of samples to visualize
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        logger.info(f"Creating t-SNE visualization with {min(n_samples, len(embeddings))} samples")
        
        # Sample if too many
        if len(embeddings) > n_samples:
            indices = np.random.choice(len(embeddings), n_samples, replace=False)
            embeddings_sample = embeddings[indices]
            titles_sample = [titles[i] for i in indices] if titles else None
        else:
            embeddings_sample = embeddings
            titles_sample = titles
        
        # Apply t-SNE
        tsne = TSNE(n_components=2, random_state=42, perplexity=30)
        embeddings_2d = tsne.fit_transform(embeddings_sample)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        scatter = ax.scatter(
            embeddings_2d[:, 0],
            embeddings_2d[:, 1],
            c=range(len(embeddings_2d)),
            cmap='viridis',
            alpha=0.6,
            s=50
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('t-SNE Component 1', fontsize=12)
        ax.set_ylabel('t-SNE Component 2', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Document Index', fontsize=10)
        
        plt.tight_layout()
        logger.info("Created t-SNE visualization")
        
        return fig
    
    def plot_search_results_quality(
        self,
        results: List[Dict[str, Any]],
        title: str = "Search Results Analysis"
    ) -> plt.Figure:
        """
        Visualize search result quality metrics.
        
        Args:
            results: List of search result dictionaries
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        if not results:
            logger.warning("No results to visualize")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No Results', ha='center', va='center', fontsize=20)
            return fig
        
        # Extract scores
        scores = [r['similarity_score'] for r in results]
        ranks = list(range(1, len(scores) + 1))
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Score by Rank
        ax1.bar(ranks, scores, color=self.colors[0], edgecolor='black', alpha=0.7)
        ax1.set_xlabel('Rank', fontsize=12)
        ax1.set_ylabel('Similarity Score', fontsize=12)
        ax1.set_title('Score Distribution by Rank', fontsize=12, fontweight='bold')
        ax1.set_xticks(ranks)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Cumulative score
        cumulative_scores = np.cumsum(scores)
        ax2.plot(ranks, cumulative_scores, marker='o', linewidth=2, 
                markersize=8, color=self.colors[1])
        ax2.set_xlabel('Number of Results', fontsize=12)
        ax2.set_ylabel('Cumulative Score', fontsize=12)
        ax2.set_title('Cumulative Score Analysis', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        logger.info("Created search quality visualization")
        
        return fig
    
    def plot_precision_recall_curve(
        self,
        precision_values: List[float],
        recall_values: List[float],
        title: str = "Precision-Recall Curve"
    ) -> plt.Figure:
        """
        Plot precision-recall curve.
        
        Args:
            precision_values: List of precision values at different k
            recall_values: List of recall values at different k
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        ax.plot(recall_values, precision_values, marker='o', 
               linewidth=2, markersize=8, color=self.colors[0])
        
        ax.set_xlabel('Recall', fontsize=12)
        ax.set_ylabel('Precision', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add area under curve annotation
        auc = np.trapz(precision_values, recall_values)
        ax.annotate(f'AUC: {auc:.3f}', xy=(0.5, 0.5), xycoords='axes fraction',
                   fontsize=12, bbox=dict(boxstyle="round", facecolor="wheat"))
        
        plt.tight_layout()
        logger.info("Created precision-recall curve")
        
        return fig
    
    def create_evaluation_dashboard(
        self,
        metrics: Dict[str, float],
        save_path: str = None
    ) -> plt.Figure:
        """
        Create a dashboard of evaluation metrics.
        
        Args:
            metrics: Dictionary of metric names and values
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # Metric 1: Bar chart of all metrics
        ax1 = axes[0, 0]
        metric_names = list(metrics.keys())
        metric_values = list(metrics.values())
        
        bars = ax1.barh(metric_names, metric_values, color=self.colors[:len(metrics)])
        ax1.set_xlabel('Score', fontsize=12)
        ax1.set_title('Evaluation Metrics Overview', fontsize=12, fontweight='bold')
        ax1.set_xlim(0, 1)
        
        # Add value labels
        for bar, value in zip(bars, metric_values):
            ax1.text(value + 0.02, bar.get_y() + bar.get_height()/2, 
                    f'{value:.3f}', va='center', fontsize=10)
        
        # Metric 2: Heatmap-style visualization
        ax2 = axes[0, 1]
        data_matrix = np.array(metric_values).reshape(1, -1)
        im = ax2.imshow(data_matrix, cmap='YlGnBu', aspect='auto')
        ax2.set_yticks([])
        ax2.set_xticks(range(len(metric_names)))
        ax2.set_xticklabels(metric_names, rotation=45, ha='right')
        ax2.set_title('Metric Heatmap', fontsize=12, fontweight='bold')
        
        # Add annotations
        for i, val in enumerate(metric_values):
            ax2.text(i, 0, f'{val:.3f}', ha='center', va='center', 
                    fontsize=10, fontweight='bold')
        
        # Metric 3: Gauge chart simulation (using pie chart)
        ax3 = axes[1, 0]
        avg_metric = np.mean(metric_values)
        
        sizes = [avg_metric, 1 - avg_metric]
        colors = ['#4CAF50', '#E0E0E0']
        
        wedges, texts = ax3.pie(sizes, colors=colors, startangle=90, counterclock=False)
        ax3.text(0, 0, f'{avg_metric:.2f}', ha='center', va='center', 
                fontsize=20, fontweight='bold')
        ax3.set_title('Average Performance', fontsize=12, fontweight='bold')
        
        # Metric 4: Table of values
        ax4 = axes[1, 1]
        ax4.axis('tight')
        ax4.axis('off')
        
        table_data = [[name, f'{value:.4f}'] for name, value in metrics.items()]
        table = ax4.table(cellText=table_data, colLabels=['Metric', 'Value'],
                         loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.5)
        
        plt.suptitle('Search Engine Evaluation Dashboard', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved evaluation dashboard to {save_path}")
        
        logger.info("Created evaluation dashboard")
        
        return fig


def visualize_embeddings_2d(
    embeddings: np.ndarray,
    method: str = 'tsne',
    **kwargs
) -> plt.Figure:
    """
    Convenience function to visualize embeddings in 2D.
    
    Args:
        embeddings: Embedding matrix
        method: Reduction method ('tsne' or 'pca')
        **kwargs: Additional arguments
        
    Returns:
        Matplotlib figure
    """
    visualizer = SearchVisualizer()
    
    if method == 'tsne':
        return visualizer.plot_embedding_tsne(embeddings, **kwargs)
    elif method == 'pca':
        from sklearn.decomposition import PCA
        
        pca = PCA(n_components=2, random_state=42)
        embeddings_2d = pca.fit_transform(embeddings)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], 
                  alpha=0.6, s=50)
        ax.set_title('PCA Visualization of Embeddings')
        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
        ax.grid(True, alpha=0.3)
        
        return fig
    else:
        raise ValueError(f"Unknown method: {method}")
