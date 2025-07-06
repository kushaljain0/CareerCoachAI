"""
Integration tests for FastAPI server endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the app after setting up the path
from mcp_server.server import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test cases for health check endpoint."""
    
    def test_health_check_success(self):
        """Test successful health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "llm_available" in data
        assert "llm_providers" in data
        assert data["status"] == "healthy"
    
    @patch('mcp_server.server.llm_client')
    def test_health_check_with_llm_info(self, mock_llm_client):
        """Test health check with LLM provider information."""
        mock_llm_client.is_available.return_value = True
        mock_llm_client.get_provider_info.return_value = {
            "default_llm": "gemini",
            "gemini_available": True,
            "openai_available": False
        }
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["llm_available"] is True
        assert "gemini" in str(data["llm_providers"])


class TestRootEndpoint:
    """Test cases for root endpoint."""
    
    def test_root_endpoint_success(self):
        """Test successful root endpoint response."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "tools" in data
        assert "resources" in data
        assert "llm_status" in data
        assert data["service"] == "Career Coach AI MCP Server"
        assert data["version"] == "1.0.0"
    
    @patch('mcp_server.server.llm_client')
    def test_root_endpoint_with_llm_status(self, mock_llm_client):
        """Test root endpoint with LLM status information."""
        mock_llm_client.is_available.return_value = True
        mock_llm_client.get_provider_info.return_value = {
            "default_llm": "openai",
            "openai_available": True
        }
        
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["llm_status"]["default_llm"] == "openai"


class TestResumeAnalysisEndpoint:
    """Test cases for resume analysis endpoint."""
    
    def test_analyze_resume_success(self):
        """Test successful resume analysis."""
        resume_text = """
        JOHN DOE
        Software Engineer
        john.doe@email.com | (555) 123-4567
        
        SUMMARY
        Experienced software engineer with 3 years developing web applications.
        
        EXPERIENCE
        Software Engineer, Tech Corp (2021-2024)
        - Developed React applications for client projects
        - Collaborated with team of 5 developers
        - Implemented new features and bug fixes
        
        SKILLS
        JavaScript, React, Python, SQL, Git
        """
        
        response = client.post("/tools/analyze_resume", json={
            "resume_text": resume_text,
            "use_llm": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "feedback" in data
        assert "analysis_type" in data
        assert "resume_length" in data
        assert data["analysis_type"] == "rule_based"
        assert data["resume_length"] == len(resume_text)
        assert isinstance(data["feedback"], list)
    
    @patch('mcp_server.server.llm_client')
    def test_analyze_resume_with_llm(self, mock_llm_client):
        """Test resume analysis with LLM enhancement."""
        mock_llm_client.is_available.return_value = True
        mock_llm_client.generate_response.return_value = "This is a comprehensive LLM analysis of your resume."
        
        resume_text = "Sample resume content"
        
        response = client.post("/tools/analyze_resume", json={
            "resume_text": resume_text,
            "use_llm": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_type"] == "llm_enhanced"
        assert "comprehensive LLM analysis" in data["feedback"]
    
    def test_analyze_resume_empty_text(self):
        """Test resume analysis with empty text."""
        response = client.post("/tools/analyze_resume", json={
            "resume_text": "",
            "use_llm": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["resume_length"] == 0
    
    def test_analyze_resume_missing_text(self):
        """Test resume analysis with missing text field."""
        response = client.post("/tools/analyze_resume", json={
            "use_llm": False
        })
        
        assert response.status_code == 422  # Validation error
    
    @patch('mcp_server.server.llm_client')
    def test_analyze_resume_llm_error(self, mock_llm_client):
        """Test resume analysis when LLM fails."""
        mock_llm_client.is_available.return_value = True
        mock_llm_client.generate_response.side_effect = Exception("LLM error")
        
        response = client.post("/tools/analyze_resume", json={
            "resume_text": "Sample resume",
            "use_llm": True
        })
        
        assert response.status_code == 500
        assert "Resume analysis failed" in response.json()["detail"]


class TestMockInterviewEndpoint:
    """Test cases for mock interview endpoint."""
    
    def test_mock_interview_success(self):
        """Test successful mock interview generation."""
        response = client.post("/tools/mock_interview", json={
            "position": "software engineer",
            "use_llm": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert "position" in data
        assert "generation_type" in data
        assert data["position"] == "software engineer"
        assert data["generation_type"] == "predefined"
        assert isinstance(data["questions"], list)
        assert len(data["questions"]) > 0
    
    @patch('mcp_server.server.llm_client')
    def test_mock_interview_with_llm(self, mock_llm_client):
        """Test mock interview with LLM enhancement."""
        mock_llm_client.is_available.return_value = True
        mock_llm_client.generate_response.return_value = "1. Tell me about yourself\n2. Describe a challenging project"
        
        response = client.post("/tools/mock_interview", json={
            "position": "data scientist",
            "use_llm": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["generation_type"] == "llm_enhanced"
        assert "Tell me about yourself" in data["questions"]
    
    def test_mock_interview_different_positions(self):
        """Test mock interview for different positions."""
        positions = ["data scientist", "product manager", "marketing manager"]
        
        for position in positions:
            response = client.post("/tools/mock_interview", json={
                "position": position,
                "use_llm": False
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["position"] == position
            assert len(data["questions"]) > 0
    
    def test_mock_interview_missing_position(self):
        """Test mock interview with missing position field."""
        response = client.post("/tools/mock_interview", json={
            "use_llm": False
        })
        
        assert response.status_code == 422  # Validation error
    
    @patch('mcp_server.server.llm_client')
    def test_mock_interview_llm_error(self, mock_llm_client):
        """Test mock interview when LLM fails."""
        mock_llm_client.is_available.return_value = True
        mock_llm_client.generate_response.side_effect = Exception("LLM error")
        
        response = client.post("/tools/mock_interview", json={
            "position": "software engineer",
            "use_llm": True
        })
        
        assert response.status_code == 500
        assert "Mock interview generation failed" in response.json()["detail"]


class TestCareerGuidesEndpoint:
    """Test cases for career guides endpoint."""
    
    @patch('mcp_server.server.retrieve')
    def test_career_guides_success(self, mock_retrieve):
        """Test successful career guides retrieval."""
        mock_retrieve.return_value = [
            {
                "chunk": "Sample career guide content about salary negotiation",
                "metadata": {"file": "salary_negotiation_guide.md"},
                "score": 0.85
            }
        ]
        
        response = client.post("/resources/career_guides/featured", json={
            "query": "salary negotiation tips",
            "top_k": 3,
            "use_llm": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "tips" in data
        assert "sources" in data
        assert "query" in data
        assert data["query"] == "salary negotiation tips"
        assert data["generation_type"] == "rag_based"
    
    @patch('mcp_server.server.retrieve')
    @patch('mcp_server.server.llm_client')
    def test_career_guides_with_llm(self, mock_llm_client, mock_retrieve):
        """Test career guides with LLM enhancement."""
        mock_retrieve.return_value = [
            {
                "chunk": "Sample content",
                "metadata": {"file": "guide.md"},
                "score": 0.8
            }
        ]
        mock_llm_client.is_available.return_value = True
        mock_llm_client.generate_response.return_value = "Enhanced career tips based on the retrieved content."
        
        response = client.post("/resources/career_guides/featured", json={
            "query": "interview preparation",
            "top_k": 2,
            "use_llm": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["generation_type"] == "llm_enhanced"
        assert "Enhanced career tips" in data["tips"]
    
    @patch('mcp_server.server.retrieve')
    def test_career_guides_no_results(self, mock_retrieve):
        """Test career guides when no results are found."""
        mock_retrieve.return_value = []
        
        response = client.post("/resources/career_guides/featured", json={
            "query": "nonexistent topic",
            "top_k": 3,
            "use_llm": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "No relevant career guides found" in data["tips"]
    
    def test_career_guides_missing_query(self):
        """Test career guides with missing query field."""
        response = client.post("/resources/career_guides/featured", json={
            "top_k": 3,
            "use_llm": False
        })
        
        assert response.status_code == 422  # Validation error


class TestChatEndpoint:
    """Test cases for chat endpoint."""
    
    @patch('mcp_server.server.llm_client')
    def test_chat_success(self, mock_llm_client):
        """Test successful chat interaction."""
        mock_llm_client.is_available.return_value = True
        mock_llm_client.generate_response.return_value = "I can help you with your career questions. What specific area would you like to focus on?"
        
        response = client.post("/chat", json={
            "message": "Can you help me with my career?",
            "use_rag": False,
            "use_tools": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "reasoning" in data
        assert "suggested_action" in data
        assert "career questions" in data["response"]
    
    @patch('mcp_server.server.retrieve')
    @patch('mcp_server.server.llm_client')
    def test_chat_with_rag(self, mock_llm_client, mock_retrieve):
        """Test chat with RAG enabled."""
        mock_retrieve.return_value = [
            {
                "chunk": "Resume writing tips and best practices",
                "metadata": {"file": "resume_guide.md"},
                "score": 0.9
            }
        ]
        mock_llm_client.is_available.return_value = True
        mock_llm_client.generate_response.return_value = "Based on the career guides, here are some resume tips..."
        
        response = client.post("/chat", json={
            "message": "How do I write a good resume?",
            "use_rag": True,
            "use_tools": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "resume tips" in data["response"]
        assert "sources" in data
        assert len(data["sources"]) > 0
    
    @patch('mcp_server.server.llm_client')
    def test_chat_with_tools(self, mock_llm_client):
        """Test chat with tools enabled."""
        mock_llm_client.is_available.return_value = True
        mock_llm_client.generate_response.return_value = "I can help you analyze your resume. Please share your resume text."
        
        response = client.post("/chat", json={
            "message": "I need help with my resume",
            "use_rag": False,
            "use_tools": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "resume" in data["response"].lower()
    
    def test_chat_missing_message(self):
        """Test chat with missing message field."""
        response = client.post("/chat", json={
            "use_rag": True,
            "use_tools": True
        })
        
        assert response.status_code == 422  # Validation error
    
    @patch('mcp_server.server.llm_client')
    def test_chat_llm_error(self, mock_llm_client):
        """Test chat when LLM fails."""
        mock_llm_client.is_available.return_value = True
        mock_llm_client.generate_response.side_effect = Exception("LLM error")
        
        response = client.post("/chat", json={
            "message": "Hello",
            "use_rag": False,
            "use_tools": False
        })
        
        assert response.status_code == 500
        assert "Chat processing failed" in response.json()["detail"]


class TestEndpointErrorHandling:
    """Test error handling across endpoints."""
    
    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        response = client.post("/tools/analyze_resume", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        
        assert response.status_code == 422
    
    def test_nonexistent_endpoint(self):
        """Test handling of nonexistent endpoint."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test handling of wrong HTTP method."""
        response = client.get("/tools/analyze_resume")
        
        assert response.status_code == 405  # Method Not Allowed 