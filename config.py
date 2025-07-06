"""
Configuration management for Career Coach AI.
Centralizes all environment variable handling.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration management."""
    
    # LLM Configuration
    DEFAULT_LLM = os.getenv('DEFAULT_LLM', 'gemini').lower()
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # LLM Response Configuration
    DEFAULT_MAX_TOKENS = int(os.getenv('DEFAULT_MAX_TOKENS', '1000'))
    INTENT_ANALYSIS_MAX_TOKENS = int(os.getenv('INTENT_ANALYSIS_MAX_TOKENS', '100'))
    
    # RAG Configuration
    DATA_DIR = os.getenv('DATA_DIR', './data')
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './data/vector_db')
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', '5'))
    CHAT_RAG_TOP_K = int(os.getenv('CHAT_RAG_TOP_K', '3'))
    
    # Server Configuration
    MCP_SERVER_HOST = os.getenv('MCP_SERVER_HOST', '0.0.0.0')
    MCP_SERVER_PORT = int(os.getenv('MCP_SERVER_PORT', '8000'))
    
    # Frontend Configuration
    VITE_API_BASE_URL = os.getenv('VITE_API_BASE_URL', 'http://localhost:8000')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_llm_config(cls):
        """Get LLM configuration as a dictionary."""
        return {
            'default_llm': cls.DEFAULT_LLM,
            'gemini_model': cls.GEMINI_MODEL,
            'openai_model': cls.OPENAI_MODEL,
            'default_max_tokens': cls.DEFAULT_MAX_TOKENS,
            'intent_analysis_max_tokens': cls.INTENT_ANALYSIS_MAX_TOKENS
        }
    
    @classmethod
    def get_rag_config(cls):
        """Get RAG configuration as a dictionary."""
        return {
            'data_dir': cls.DATA_DIR,
            'vector_db_path': cls.VECTOR_DB_PATH,
            'chunk_size': cls.CHUNK_SIZE,
            'chunk_overlap': cls.CHUNK_OVERLAP,
            'embedding_model': cls.EMBEDDING_MODEL,
            'top_k_results': cls.TOP_K_RESULTS,
            'chat_rag_top_k': cls.CHAT_RAG_TOP_K
        }
    
    @classmethod
    def get_server_config(cls):
        """Get server configuration as a dictionary."""
        return {
            'host': cls.MCP_SERVER_HOST,
            'port': cls.MCP_SERVER_PORT,
            'log_level': cls.LOG_LEVEL
        }
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present."""
        errors = []
        
        if not cls.GOOGLE_API_KEY and cls.DEFAULT_LLM == 'gemini':
            errors.append("GOOGLE_API_KEY is required when DEFAULT_LLM is 'gemini'")
        
        if not cls.OPENAI_API_KEY and cls.DEFAULT_LLM == 'openai':
            errors.append("OPENAI_API_KEY is required when DEFAULT_LLM is 'openai'")
        
        if not cls.GOOGLE_API_KEY and not cls.OPENAI_API_KEY:
            errors.append("At least one API key (GOOGLE_API_KEY or OPENAI_API_KEY) is required")
        
        return errors 