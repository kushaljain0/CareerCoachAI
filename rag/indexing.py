import os
import glob
import pickle
from typing import List, Dict
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss

# Load environment variables
load_dotenv()

DATA_DIR = os.getenv('DATA_DIR', './data')
VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './data/vector_db')
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# Load embedding model
model = SentenceTransformer(EMBEDDING_MODEL)

def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks

def load_documents(data_dir: str) -> List[Dict]:
    docs = []
    for file_path in glob.glob(os.path.join(data_dir, '*.md')):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        docs.append({'file': os.path.basename(file_path), 'text': text})
    return docs

def main():
    docs = load_documents(DATA_DIR)
    all_chunks = []
    metadata = []
    for doc in docs:
        chunks = chunk_text(doc['text'], CHUNK_SIZE, CHUNK_OVERLAP)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            metadata.append({'file': doc['file'], 'chunk_id': i})
    print(f"Total chunks: {len(all_chunks)}")
    # Embed chunks
    embeddings = model.encode(all_chunks, show_progress_bar=True, convert_to_numpy=True)
    # Build FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, os.path.join(VECTOR_DB_PATH, 'faiss.index'))
    with open(os.path.join(VECTOR_DB_PATH, 'metadata.pkl'), 'wb') as f:
        pickle.dump(metadata, f)
    with open(os.path.join(VECTOR_DB_PATH, 'chunks.pkl'), 'wb') as f:
        pickle.dump(all_chunks, f)
    print(f"Index and metadata saved to {VECTOR_DB_PATH}")

if __name__ == '__main__':
    main() 