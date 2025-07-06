"""
LLM Client for Career Coach AI
Supports Gemini (default), OpenAI, and Claude with unified interface.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    """Unified LLM client supporting multiple providers."""
    
    def __init__(self):
        self.default_llm = os.getenv('DEFAULT_LLM', 'gemini-2.5-flash').lower()
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.default_max_tokens = int(os.getenv('DEFAULT_MAX_TOKENS', '1000'))
        
        # Initialize clients
        self.gemini_client = None
        self.openai_client = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize LLM clients based on available API keys."""
        try:
            if os.getenv('GOOGLE_API_KEY'):
                import google.generativeai as genai
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                self.gemini_client = genai.GenerativeModel(self.gemini_model)
                logger.info(f"Gemini client initialized with model: {self.gemini_model}")
        except ImportError:
            logger.warning("google-generativeai not installed. Gemini unavailable.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
        
        try:
            if os.getenv('OPENAI_API_KEY'):
                import openai
                self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                logger.info(f"OpenAI client initialized with model: {self.openai_model}")
        except ImportError:
            logger.warning("openai not installed. OpenAI unavailable.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def generate_response(self, prompt: str, max_tokens: int = None) -> str:
        """
        Generate response using the preferred LLM with fallback.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens for response (uses DEFAULT_MAX_TOKENS if not specified)
            
        Returns:
            Generated response text
        """
        # Use default max_tokens if not specified
        if max_tokens is None:
            max_tokens = self.default_max_tokens
            
        # Try default LLM first
        if self.default_llm == 'gemini-2.5-flash' and self.gemini_client:
            try:
                response = self.gemini_client.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.warning(f"Gemini failed, trying fallback: {e}")
        
        if self.default_llm == 'gemini-2.5-pro' and self.gemini_client:
            try:
                response = self.gemini_client.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.warning(f"Gemini failed, trying fallback: {e}")

        # Fallback to OpenAI
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI fallback failed: {e}")
        
        # If all LLMs fail, return a default response
        logger.error("All LLM providers failed. Using default response.")
        return self._get_default_response(prompt)
    
    def _get_default_response(self, prompt: str) -> str:
        """Provide a default response when LLM is unavailable."""
        if "resume" in prompt.lower():
            return "I'm currently unable to analyze resumes due to technical issues. Please try again later or contact support."
        elif "interview" in prompt.lower():
            return "I'm currently unable to generate interview questions due to technical issues. Please try again later."
        else:
            return "I'm currently experiencing technical difficulties. Please try again later or contact support."
    
    def is_available(self) -> bool:
        """Check if any LLM provider is available."""
        return bool(self.gemini_client or self.openai_client)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available providers."""
        return {
            "default_llm": self.default_llm,
            "gemini_available": bool(self.gemini_client),
            "openai_available": bool(self.openai_client),
            "gemini_model": self.gemini_model if self.gemini_client else None,
            "openai_model": self.openai_model if self.openai_client else None
        }

# Global LLM client instance
llm_client = LLMClient() 