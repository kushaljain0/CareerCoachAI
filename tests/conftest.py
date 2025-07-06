"""
Pytest configuration and common fixtures for CareerCoachAI tests.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    JOHN DOE
    Software Engineer
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe
    
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

@pytest.fixture
def sample_interview_position():
    """Sample interview position for testing."""
    return "data scientist"

@pytest.fixture
def sample_chat_query():
    """Sample chat query for testing."""
    return "Can you help me analyze my resume?"

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "choices": [{
            "message": {
                "content": "This is a mock response from the LLM for testing purposes."
            }
        }]
    }

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Mock response"))]
    )
    return mock_client

@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_career_guides_query():
    """Sample query for career guides testing."""
    return "salary negotiation tips"

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Set test environment
    os.environ["TESTING"] = "true"
    
    # Mock environment variables that might be required
    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = "test-key"
    
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = "test-key"
    
    yield
    
    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"] 