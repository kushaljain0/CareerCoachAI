"""
Unit tests for RAG retrieval module.
"""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
import os
import tempfile
from pathlib import Path
import sys
import numpy as np

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rag.retrieval import load_index_and_metadata, retrieve


class TestLoadIndexAndMetadata:
    """Test cases for loading index and metadata."""
    
    @patch('rag.retrieval.faiss.read_index')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pickle.load')
    def test_load_index_and_metadata_success(self, mock_pickle_load, mock_file, mock_read_index):
        """Test successful loading of index and metadata."""
        # Mock FAISS index
        mock_index = Mock()
        mock_read_index.return_value = mock_index
        
        # Mock metadata and chunks
        mock_metadata = [{'file': 'doc1.md', 'chunk_id': 0}, {'file': 'doc2.md', 'chunk_id': 1}]
        mock_chunks = ['chunk 1 content', 'chunk 2 content']
        mock_pickle_load.side_effect = [mock_metadata, mock_chunks]
        
        # Mock file context manager
        mock_file.return_value.__enter__.return_value = mock_file.return_value
        
        with patch.dict(os.environ, {'VECTOR_DB_PATH': '/test/vector_db'}):
            index, metadata, chunks = load_index_and_metadata()
        
        assert index == mock_index
        assert metadata == mock_metadata
        assert chunks == mock_chunks
        
        # Verify file paths
        expected_metadata_path = '/test/vector_db/metadata.pkl'
        expected_chunks_path = '/test/vector_db/chunks.pkl'
        expected_index_path = '/test/vector_db/faiss.index'
        
        mock_read_index.assert_called_once_with(expected_index_path)
        assert mock_file.call_count == 2  # metadata and chunks files
    
    @patch('rag.retrieval.faiss.read_index')
    def test_load_index_and_metadata_file_not_found(self, mock_read_index):
        """Test handling of missing index file."""
        mock_read_index.side_effect = FileNotFoundError("Index file not found")
        
        with patch.dict(os.environ, {'VECTOR_DB_PATH': '/test/vector_db'}):
            with pytest.raises(FileNotFoundError, match="Index file not found"):
                load_index_and_metadata()
    
    @patch('rag.retrieval.faiss.read_index')
    @patch('builtins.open', side_effect=FileNotFoundError("Metadata file not found"))
    def test_load_index_and_metadata_metadata_not_found(self, mock_file, mock_read_index):
        """Test handling of missing metadata file."""
        mock_index = Mock()
        mock_read_index.return_value = mock_index
        
        with patch.dict(os.environ, {'VECTOR_DB_PATH': '/test/vector_db'}):
            with pytest.raises(FileNotFoundError, match="Metadata file not found"):
                load_index_and_metadata()


class TestRetrieve:
    """Test cases for retrieval functionality."""
    
    @patch('rag.retrieval.load_index_and_metadata')
    @patch('rag.retrieval.SentenceTransformer')
    def test_retrieve_basic(self, mock_sentence_transformer, mock_load_index):
        """Test basic retrieval functionality."""
        # Mock sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_sentence_transformer.return_value = mock_model
        
        # Mock FAISS index and metadata
        mock_index = Mock()
        mock_index.search.return_value = (np.array([[0.1, 0.2]]), np.array([[0, 1]]))
        mock_metadata = [{'file': 'doc1.md', 'chunk_id': 0}, {'file': 'doc2.md', 'chunk_id': 1}]
        mock_chunks = ['chunk 1 content', 'chunk 2 content']
        mock_load_index.return_value = (mock_index, mock_metadata, mock_chunks)
        
        with patch.dict(os.environ, {'TOP_K_RESULTS': '5'}):
            results = retrieve("test query", top_k=2)
        
        assert len(results) == 2
        assert results[0]['chunk'] == 'chunk 1 content'
        assert results[0]['metadata']['file'] == 'doc1.md'
        assert results[1]['chunk'] == 'chunk 2 content'
        assert results[1]['metadata']['file'] == 'doc2.md'
        
        # Verify function calls
        mock_model.encode.assert_called_once()
        mock_index.search.assert_called_once()
    
    @patch('rag.retrieval.load_index_and_metadata')
    @patch('rag.retrieval.SentenceTransformer')
    def test_retrieve_with_multi_query(self, mock_sentence_transformer, mock_load_index):
        """Test retrieval with multi-query reformulation."""
        # Mock sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_sentence_transformer.return_value = mock_model
        
        # Mock FAISS index and metadata
        mock_index = Mock()
        mock_index.search.return_value = (np.array([[0.1, 0.2]]), np.array([[0, 1]]))
        mock_metadata = [{'file': 'doc1.md', 'chunk_id': 0}, {'file': 'doc2.md', 'chunk_id': 1}]
        mock_chunks = ['chunk 1 content', 'chunk 2 content']
        mock_load_index.return_value = (mock_index, mock_metadata, mock_chunks)
        
        # Mock paraphrasing pipeline
        mock_paraphraser = Mock()
        mock_paraphraser.return_value = [
            {'generated_text': 'alternative query 1'},
            {'generated_text': 'alternative query 2'}
        ]
        
        with patch('rag.retrieval.pipeline', return_value=mock_paraphraser), \
             patch.dict(os.environ, {'TOP_K_RESULTS': '5'}):
            results = retrieve("test query", top_k=2, multi_query=True)
        
        # Should have results from multiple queries
        assert len(results) >= 2
        mock_index.search.assert_called()  # Called for each query
    
    @patch('rag.retrieval.load_index_and_metadata')
    @patch('rag.retrieval.SentenceTransformer')
    def test_retrieve_multi_query_fallback(self, mock_sentence_transformer, mock_load_index):
        """Test retrieval when paraphrasing fails."""
        # Mock sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_sentence_transformer.return_value = mock_model
        
        # Mock FAISS index and metadata
        mock_index = Mock()
        mock_index.search.return_value = (np.array([[0.1, 0.2]]), np.array([[0, 1]]))
        mock_metadata = [{'file': 'doc1.md', 'chunk_id': 0}, {'file': 'doc2.md', 'chunk_id': 1}]
        mock_chunks = ['chunk 1 content', 'chunk 2 content']
        mock_load_index.return_value = (mock_index, mock_metadata, mock_chunks)
        
        # Mock paraphrasing to fail
        with patch('rag.retrieval.pipeline', side_effect=Exception("Paraphrasing failed")), \
             patch.dict(os.environ, {'TOP_K_RESULTS': '5'}):
            results = retrieve("test query", top_k=2, multi_query=True)
        
        # Should still work with single query
        assert len(results) == 2
        mock_index.search.assert_called_once()  # Called only once for original query
    
    @patch('rag.retrieval.load_index_and_metadata')
    @patch('rag.retrieval.SentenceTransformer')
    def test_retrieve_deduplication(self, mock_sentence_transformer, mock_load_index):
        """Test that duplicate results are removed."""
        # Mock sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_sentence_transformer.return_value = mock_model
        
        # Mock FAISS index and metadata with duplicates
        mock_index = Mock()
        mock_index.search.return_value = (np.array([[0.1, 0.2, 0.1]]), np.array([[0, 1, 0]]))
        mock_metadata = [
            {'file': 'doc1.md', 'chunk_id': 0},
            {'file': 'doc2.md', 'chunk_id': 1},
            {'file': 'doc1.md', 'chunk_id': 0}  # Duplicate
        ]
        mock_chunks = ['chunk 1 content', 'chunk 2 content', 'chunk 1 content']
        mock_load_index.return_value = (mock_index, mock_metadata, mock_chunks)
        
        with patch.dict(os.environ, {'TOP_K_RESULTS': '5'}):
            results = retrieve("test query", top_k=3)
        
        # Should have deduplicated results
        assert len(results) == 2  # Only unique results
        assert results[0]['metadata']['file'] == 'doc1.md'
        assert results[1]['metadata']['file'] == 'doc2.md'
    
    @patch('rag.retrieval.load_index_and_metadata')
    @patch('rag.retrieval.SentenceTransformer')
    def test_retrieve_empty_results(self, mock_sentence_transformer, mock_load_index):
        """Test retrieval when no results are found."""
        # Mock sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_sentence_transformer.return_value = mock_model
        
        # Mock FAISS index with no results
        mock_index = Mock()
        mock_index.search.return_value = (np.array([[]]), np.array([[]]))
        mock_metadata = []
        mock_chunks = []
        mock_load_index.return_value = (mock_index, mock_metadata, mock_chunks)
        
        with patch.dict(os.environ, {'TOP_K_RESULTS': '5'}):
            results = retrieve("test query", top_k=5)
        
        assert results == []
    
    @patch('rag.retrieval.load_index_and_metadata')
    @patch('rag.retrieval.SentenceTransformer')
    def test_retrieve_respects_top_k(self, mock_sentence_transformer, mock_load_index):
        """Test that retrieval respects the top_k parameter."""
        # Mock sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_sentence_transformer.return_value = mock_model
        
        # Mock FAISS index with many results
        mock_index = Mock()
        mock_index.search.return_value = (np.array([[0.1, 0.2, 0.3, 0.4, 0.5]]), np.array([[0, 1, 2, 3, 4]]))
        mock_metadata = [
            {'file': 'doc1.md', 'chunk_id': 0},
            {'file': 'doc2.md', 'chunk_id': 1},
            {'file': 'doc3.md', 'chunk_id': 2},
            {'file': 'doc4.md', 'chunk_id': 3},
            {'file': 'doc5.md', 'chunk_id': 4}
        ]
        mock_chunks = ['chunk 1', 'chunk 2', 'chunk 3', 'chunk 4', 'chunk 5']
        mock_load_index.return_value = (mock_index, mock_metadata, mock_chunks)
        
        with patch.dict(os.environ, {'TOP_K_RESULTS': '5'}):
            results = retrieve("test query", top_k=3)
        
        assert len(results) == 3  # Should respect top_k=3
    
    @patch('rag.retrieval.load_index_and_metadata')
    @patch('rag.retrieval.SentenceTransformer')
    def test_retrieve_environment_variables(self, mock_sentence_transformer, mock_load_index):
        """Test that environment variables are used correctly."""
        # Mock sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_sentence_transformer.return_value = mock_model
        
        # Mock FAISS index and metadata
        mock_index = Mock()
        mock_index.search.return_value = (np.array([[0.1]]), np.array([[0]]))
        mock_metadata = [{'file': 'doc1.md', 'chunk_id': 0}]
        mock_chunks = ['chunk 1 content']
        mock_load_index.return_value = (mock_index, mock_metadata, mock_chunks)
        
        with patch.dict(os.environ, {
            'TOP_K_RESULTS': '10',
            'EMBEDDING_MODEL': 'test-model'
        }):
            results = retrieve("test query")  # Should use TOP_K_RESULTS=10
        
        assert len(results) == 1
        mock_sentence_transformer.assert_called_once_with('test-model')


class TestRetrieveEdgeCases:
    """Test edge cases and error handling."""
    
    @patch('rag.retrieval.load_index_and_metadata')
    def test_retrieve_loading_error(self, mock_load_index):
        """Test handling of index loading errors."""
        mock_load_index.side_effect = FileNotFoundError("Index not found")
        
        with pytest.raises(FileNotFoundError, match="Index not found"):
            retrieve("test query")
    
    @patch('rag.retrieval.load_index_and_metadata')
    @patch('rag.retrieval.SentenceTransformer')
    def test_retrieve_encoding_error(self, mock_sentence_transformer, mock_load_index):
        """Test handling of encoding errors."""
        mock_model = Mock()
        mock_model.encode.side_effect = Exception("Encoding failed")
        mock_sentence_transformer.return_value = mock_model
        
        mock_index = Mock()
        mock_metadata = []
        mock_chunks = []
        mock_load_index.return_value = (mock_index, mock_metadata, mock_chunks)
        
        with pytest.raises(Exception, match="Encoding failed"):
            retrieve("test query")
    
    @patch('rag.retrieval.load_index_and_metadata')
    @patch('rag.retrieval.SentenceTransformer')
    def test_retrieve_search_error(self, mock_sentence_transformer, mock_load_index):
        """Test handling of FAISS search errors."""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_sentence_transformer.return_value = mock_model
        
        mock_index = Mock()
        mock_index.search.side_effect = Exception("Search failed")
        mock_metadata = []
        mock_chunks = []
        mock_load_index.return_value = (mock_index, mock_metadata, mock_chunks)
        
        with pytest.raises(Exception, match="Search failed"):
            retrieve("test query") 