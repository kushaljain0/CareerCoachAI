import os
import pickle
from typing import List, Dict
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss

load_dotenv()

VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './data/vector_db')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', 5))

model = SentenceTransformer(EMBEDDING_MODEL)

# Helper to load index and metadata
def load_index_and_metadata():
    index = faiss.read_index(os.path.join(VECTOR_DB_PATH, 'faiss.index'))
    with open(os.path.join(VECTOR_DB_PATH, 'metadata.pkl'), 'rb') as f:
        metadata = pickle.load(f)
    with open(os.path.join(VECTOR_DB_PATH, 'chunks.pkl'), 'rb') as f:
        chunks = pickle.load(f)
    return index, metadata, chunks

def retrieve(query: str, top_k: int = TOP_K_RESULTS, multi_query: bool = True) -> List[Dict]:
    index, metadata, chunks = load_index_and_metadata()
    queries = [query]
    # Multi-query reformulation (simple version: synonyms/LLM expansion)
    if multi_query:
        try:
            from transformers import pipeline
            # Use a paraphrasing model if available
            paraphraser = pipeline('text2text-generation', model='Vamsi/T5_Paraphrase_Paws')
            alt = paraphraser(query, max_length=64, num_return_sequences=2)
            queries += [x['generated_text'] for x in alt]
        except Exception:
            pass  # Fallback to single query if paraphraser not available
    all_results = []
    for q in queries:
        q_emb = model.encode([q], convert_to_numpy=True)
        D, I = index.search(q_emb, top_k)
        for i, idx in enumerate(I[0]):
            all_results.append({
                'score': float(D[0][i]),
                'chunk': chunks[idx],
                'metadata': metadata[idx],
                'query': q
            })
    # Deduplicate and sort by score
    seen = set()
    deduped = []
    for r in sorted(all_results, key=lambda x: x['score']):
        key = (r['metadata']['file'], r['metadata']['chunk_id'])
        if key not in seen:
            deduped.append(r)
            seen.add(key)
    return deduped[:top_k]

if __name__ == '__main__':
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else 'How do I improve my resume?'
    results = retrieve(query)
    for r in results:
        print(f"[{r['metadata']['file']}]: {r['chunk'][:200]}...\nScore: {r['score']:.2f}\n") 