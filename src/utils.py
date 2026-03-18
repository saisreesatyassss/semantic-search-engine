"""
Utility Functions
Helper functions for the semantic search engine
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any


def setup_logging(log_file: str = None, level: str = "INFO"):
    """
    Configure application logging
    
    Args:
        log_file: Optional path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    return logger


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Return default config if file doesn't exist
        return get_default_config()
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_default_config() -> Dict[str, Any]:
    """Get default configuration values"""
    return {
        'model': {
            'name': 'sentence-transformers/all-MiniLM-L6-v2',
            'batch_size': 32,
            'device': 'cpu'
        },
        'faiss': {
            'index_type': 'IndexFlatL2',
            'metric': 'cosine'
        },
        'search': {
            'default_top_k': 10,
            'default_threshold': 0.5
        },
        'data': {
            'raw_dir': 'data/raw',
            'processed_dir': 'data/processed',
            'embeddings_dir': 'embeddings',
            'index_dir': 'faiss_index'
        }
    }


def save_config(config: Dict[str, Any], output_path: str = "config.yaml"):
    """
    Save configuration to YAML file
    
    Args:
        config: Configuration dictionary
        output_path: Path to output file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    logging.info(f"Configuration saved to {output_file}")


def ensure_directories(base_dir: str = None):
    """
    Create necessary directories if they don't exist
    
    Args:
        base_dir: Base directory path (defaults to project root)
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent
    
    base_dir = Path(base_dir)
    
    directories = [
        base_dir / "data" / "raw",
        base_dir / "data" / "processed",
        base_dir / "embeddings",
        base_dir / "faiss_index",
        base_dir / "models" / "bert_model",
        base_dir / "logs"
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"Created {len(directories)} directories")


class Config:
    """Configuration manager class"""
    
    _instance = None
    _config = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._config:
            self._config = get_default_config()
    
    def get(self, key: str, default=None):
        """Get configuration value by dot notation"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value):
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def all(self) -> Dict[str, Any]:
        """Get entire configuration"""
        return self._config.copy()


# Convenience function
def get_config() -> Config:
    """Get global configuration instance"""
    return Config()
