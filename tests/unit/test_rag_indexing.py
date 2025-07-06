"""
Unit tests for RAG indexing module.
"""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
import os
import tempfile
from pathlib import Path
import sys

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rag.indexing import chunk_text, load_documents, main


class TestChunkText:
    """Test cases for text chunking functionality."""
    
    def test_chunk_text_basic(self):
        """Test basic text chunking."""
        text = "This is a test document with some content."
        chunks = chunk_text(text, chunk_size=10, overlap=2)
        
        assert len(chunks) > 0
        assert all(len(chunk) <= 10 for chunk in chunks)
        # Check that chunks overlap
        if len(chunks) > 1:
            assert chunks[0][-2:] in chunks[1]
    
    def test_chunk_text_smaller_than_chunk_size(self):
        """Test chunking text smaller than chunk size."""
        text = "Short text"
        chunks = chunk_text(text, chunk_size=20, overlap=5)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_text_exact_chunk_size(self):
        """Test chunking text that's exactly the chunk size."""
        text = "Exactly ten chars"
        chunks = chunk_text(text, chunk_size=10, overlap=2)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_text_with_overlap(self):
        """Test chunking with overlap."""
        text = "This is a longer text that should be chunked with overlap"
        chunks = chunk_text(text, chunk_size=15, overlap=5)
        
        assert len(chunks) > 1
        # Check overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            overlap_found = False
            for j in range(5):
                if chunks[i][-(5-j):] in chunks[i+1]:
                    overlap_found = True
                    break
            assert overlap_found, f"No overlap found between chunks {i} and {i+1}"
    
    def test_chunk_text_empty(self):
        """Test chunking empty text."""
        chunks = chunk_text("", chunk_size=10, overlap=2)
        assert chunks == []
    
    def test_chunk_text_single_character(self):
        """Test chunking single character text."""
        chunks = chunk_text("a", chunk_size=10, overlap=2)
        assert chunks == ["a"]


class TestLoadDocuments:
    """Test cases for document loading functionality."""
    
    @patch('rag.indexing.glob.glob')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_documents_success(self, mock_file, mock_glob):
        """Test successful document loading."""
        mock_glob.return_value = ['/path/to/doc1.md', '/path/to/doc2.md']
        mock_file.return_value.__enter__.return_value.read.return_value = "Document content"
        
        docs = load_documents('/test/data/dir')
        
        assert len(docs) == 2
        assert docs[0]['file'] == 'doc1.md'
        assert docs[0]['text'] == "Document content"
        assert docs[1]['file'] == 'doc2.md'
        assert docs[1]['text'] == "Document content"
        
        mock_glob.assert_called_once_with('/test/data/dir/*.md')
    
    @patch('rag.indexing.glob.glob')
    def test_load_documents_no_files(self, mock_glob):
        """Test loading documents when no files exist."""
        mock_glob.return_value = []
        
        docs = load_documents('/test/data/dir')
        
        assert docs == []
        mock_glob.assert_called_once_with('/test/data/dir/*.md')
    
    @patch('rag.indexing.glob.glob')
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_load_documents_file_error(self, mock_file, mock_glob):
        """Test handling of file reading errors."""
        mock_glob.return_value = ['/path/to/doc1.md']
        
        with pytest.raises(FileNotFoundError):
            load_documents('/test/data/dir')
    
    @patch('rag.indexing.glob.glob')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_documents_encoding(self, mock_file, mock_glob):
        """Test document loading with proper encoding."""
        mock_glob.return_value = ['/path/to/doc1.md']
        mock_file.return_value.__enter__.return_value.read.return_value = "Document content"
        
        load_documents('/test/data/dir')
        
        # Check that open was called with utf-8 encoding
        mock_file.assert_called_with('/path/to/doc1.md', 'r', encoding='utf-8')


class TestRAGIndexingIntegration:
    """Integration tests for RAG indexing."""
    
    @patch('rag.indexing.SentenceTransformer')
    @patch('rag.indexing.faiss.IndexFlatL2')
    @patch('rag.indexing.faiss.write_index')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pickle.dump')
    @patch('rag.indexing.load_documents')
    @patch('rag.indexing.chunk_text')
    def test_main_function_success(self, mock_chunk_text, mock_load_docs, 
                                 mock_pickle_dump, mock_file, mock_write_index,
                                 mock_faiss_index, mock_sentence_transformer):
        """Test successful execution of main function."""
        # Mock document loading
        mock_load_docs.return_value = [
            {'file': 'doc1.md', 'text': 'Document 1 content'},
            {'file': 'doc2.md', 'text': 'Document 2 content'}
        ]
        
        # Mock chunking
        mock_chunk_text.side_effect = lambda text, chunk_size, overlap: [text[:5], text[5:]]
        
        # Mock sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_sentence_transformer.return_value = mock_model
        
        # Mock FAISS index
        mock_index = Mock()
        mock_faiss_index.return_value = mock_index
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'DATA_DIR': '/test/data',
            'VECTOR_DB_PATH': '/test/vector_db',
            'CHUNK_SIZE': '1000',
            'CHUNK_OVERLAP': '200',
            'EMBEDDING_MODEL': 'all-MiniLM-L6-v2'
        }):
            main()
        
        # Verify function calls
        mock_load_docs.assert_called_once_with('/test/data')
        assert mock_chunk_text.call_count == 2  # Called for each document
        mock_model.encode.assert_called_once()
        mock_index.add.assert_called_once()
        mock_write_index.assert_called_once()
        assert mock_pickle_dump.call_count == 2  # metadata and chunks
    
    @patch('rag.indexing.os.makedirs')
    @patch('rag.indexing.SentenceTransformer')
    def test_main_function_creates_directories(self, mock_sentence_transformer, mock_makedirs):
        """Test that main function creates necessary directories."""
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]
        mock_sentence_transformer.return_value = mock_model
        
        with patch('rag.indexing.load_documents', return_value=[]), \
             patch('rag.indexing.faiss.IndexFlatL2'), \
             patch('rag.indexing.faiss.write_index'), \
             patch('builtins.open', new_callable=mock_open), \
             patch('pickle.dump'), \
             patch.dict(os.environ, {'VECTOR_DB_PATH': '/test/vector_db'}):
            main()
        
        mock_makedirs.assert_called_once_with('/test/vector_db', exist_ok=True)
    
    @patch('rag.indexing.SentenceTransformer')
    def test_main_function_handles_empty_documents(self, mock_sentence_transformer):
        """Test main function behavior with empty document list."""
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        
        with patch('rag.indexing.load_documents', return_value=[]), \
             patch('rag.indexing.faiss.IndexFlatL2'), \
             patch('rag.indexing.faiss.write_index'), \
             patch('builtins.open', new_callable=mock_open), \
             patch('pickle.dump'):
            main()
        
        # Should not call encode if no documents
        mock_model.encode.assert_not_called()


class TestRAGIndexingEdgeCases:
    """Test edge cases and error handling."""
    
    @patch('rag.indexing.SentenceTransformer')
    def test_main_function_model_loading_error(self, mock_sentence_transformer):
        """Test handling of model loading errors."""
        mock_sentence_transformer.side_effect = Exception("Model loading failed")
        
        with pytest.raises(Exception, match="Model loading failed"):
            main()
    
    @patch('rag.indexing.SentenceTransformer')
    @patch('rag.indexing.load_documents')
    def test_main_function_encoding_error(self, mock_load_docs, mock_sentence_transformer):
        """Test handling of encoding errors."""
        mock_load_docs.return_value = [{'file': 'doc1.md', 'text': 'content'}]
        mock_model = Mock()
        mock_model.encode.side_effect = Exception("Encoding failed")
        mock_sentence_transformer.return_value = mock_model
        
        with patch('rag.indexing.chunk_text', return_value=['content']), \
             patch('rag.indexing.faiss.IndexFlatL2'), \
             pytest.raises(Exception, match="Encoding failed"):
            main() 