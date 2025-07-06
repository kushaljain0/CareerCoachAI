"""
Unit tests for LLM client module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from mcp_server.llm_client import LLMClient


class TestLLMClient:
    """Test cases for LLMClient class."""
    
    @pytest.fixture
    def llm_client(self):
        """Create a fresh LLM client instance for each test."""
        with patch.dict(os.environ, {
            'DEFAULT_LLM': 'gemini',
            'GEMINI_MODEL': 'gemini-1.5-flash',
            'OPENAI_MODEL': 'gpt-4o-mini'
        }):
            return LLMClient()
    
    def test_initialization(self, llm_client):
        """Test LLM client initialization."""
        assert llm_client.default_llm == 'gemini'
        assert llm_client.gemini_model == 'gemini-1.5-flash'
        assert llm_client.openai_model == 'gpt-4o-mini'
    
    @patch('mcp_server.llm_client.os.getenv')
    def test_initialization_with_env_vars(self, mock_getenv):
        """Test initialization with environment variables."""
        mock_getenv.side_effect = lambda key, default=None: {
            'DEFAULT_LLM': 'openai',
            'GEMINI_MODEL': 'gemini-pro',
            'OPENAI_MODEL': 'gpt-4',
            'GOOGLE_API_KEY': 'test-gemini-key',
            'OPENAI_API_KEY': 'test-openai-key'
        }.get(key, default)
        
        with patch('google.generativeai.GenerativeModel'), \
             patch('openai.OpenAI'):
            client = LLMClient()
            assert client.default_llm == 'openai'
            assert client.gemini_model == 'gemini-pro'
            assert client.openai_model == 'gpt-4'
    
    @patch('google.generativeai.GenerativeModel')
    @patch('openai.OpenAI')
    def test_gemini_client_initialization(self, mock_openai, mock_gemini_model):
        """Test Gemini client initialization."""
        mock_gemini_model.return_value = Mock()
        
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-key'}):
            client = LLMClient()
            assert client.gemini_client is not None
            mock_gemini_model.assert_called_once_with('gemini-1.5-flash')
    
    @patch('openai.OpenAI')
    @patch('google.generativeai.GenerativeModel')
    def test_openai_client_initialization(self, mock_gemini_model, mock_openai):
        """Test OpenAI client initialization."""
        mock_openai.return_value = Mock()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient()
            assert client.openai_client is not None
            mock_openai.assert_called_once_with(api_key='test-key')
    
    @patch('google.generativeai.GenerativeModel')
    def test_gemini_response_generation(self, mock_gemini_model):
        """Test response generation using Gemini."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "This is a test response from Gemini"
        mock_model.generate_content.return_value = mock_response
        mock_gemini_model.return_value = mock_model
        
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-key'}):
            client = LLMClient()
            response = client.generate_response("Test prompt")
            
            assert response == "This is a test response from Gemini"
            mock_model.generate_content.assert_called_once_with("Test prompt")
    
    @patch('openai.OpenAI')
    def test_openai_response_generation(self, mock_openai):
        """Test response generation using OpenAI."""
        mock_client = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "This is a test response from OpenAI"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient()
            client.default_llm = 'openai'
            response = client.generate_response("Test prompt")
            
            assert response == "This is a test response from OpenAI"
            mock_client.chat.completions.create.assert_called_once()
    
    def test_gemini_fallback_to_openai(self, llm_client):
        """Test fallback from Gemini to OpenAI when Gemini fails."""
        # Mock Gemini to fail
        llm_client.gemini_client = Mock()
        llm_client.gemini_client.generate_content.side_effect = Exception("Gemini error")
        
        # Mock OpenAI to succeed
        mock_openai_response = Mock()
        mock_openai_response.choices = [Mock(message=Mock(content="OpenAI fallback response"))]
        llm_client.openai_client = Mock()
        llm_client.openai_client.chat.completions.create.return_value = mock_openai_response
        
        response = llm_client.generate_response("Test prompt")
        
        assert response == "OpenAI fallback response"
        llm_client.gemini_client.generate_content.assert_called_once()
        llm_client.openai_client.chat.completions.create.assert_called_once()
    
    def test_default_response_when_all_llms_fail(self, llm_client):
        """Test default response when all LLM providers fail."""
        llm_client.gemini_client = None
        llm_client.openai_client = None
        
        # Test resume-related prompt
        response = llm_client.generate_response("Can you analyze my resume?")
        assert "resume" in response.lower()
        assert "unable" in response.lower()
        
        # Test interview-related prompt
        response = llm_client.generate_response("Generate interview questions")
        assert "interview" in response.lower()
        assert "unable" in response.lower()
        
        # Test general prompt
        response = llm_client.generate_response("General question")
        assert "technical difficulties" in response.lower()
    
    def test_is_available(self, llm_client):
        """Test availability check."""
        # No clients available
        llm_client.gemini_client = None
        llm_client.openai_client = None
        assert not llm_client.is_available()
        
        # Gemini available
        llm_client.gemini_client = Mock()
        assert llm_client.is_available()
        
        # OpenAI available
        llm_client.gemini_client = None
        llm_client.openai_client = Mock()
        assert llm_client.is_available()
    
    def test_get_provider_info(self, llm_client):
        """Test provider information retrieval."""
        llm_client.gemini_client = Mock()
        llm_client.openai_client = None
        
        info = llm_client.get_provider_info()
        
        assert info['default_llm'] == 'gemini'
        assert info['gemini_available'] is True
        assert info['openai_available'] is False
        assert info['gemini_model'] == 'gemini-1.5-flash'
        assert info['openai_model'] is None
    
    def test_max_tokens_parameter(self, llm_client):
        """Test max_tokens parameter is passed correctly."""
        llm_client.openai_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        llm_client.openai_client.chat.completions.create.return_value = mock_response
        
        llm_client.generate_response("Test prompt", max_tokens=500)
        
        call_args = llm_client.openai_client.chat.completions.create.call_args
        assert call_args[1]['max_tokens'] == 500


class TestLLMClientIntegration:
    """Integration tests for LLM client with real environment."""
    
    @pytest.mark.integration
    def test_client_initialization_without_keys(self):
        """Test client initialization without API keys."""
        with patch.dict(os.environ, {}, clear=True):
            client = LLMClient()
            assert client.gemini_client is None
            assert client.openai_client is None
            assert not client.is_available()
    
    @pytest.mark.integration
    def test_default_response_behavior(self):
        """Test default response behavior without LLM access."""
        with patch.dict(os.environ, {}, clear=True):
            client = LLMClient()
            response = client.generate_response("Test prompt")
            assert "technical difficulties" in response.lower() 