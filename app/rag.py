import os
import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple

INDEX_PATH = Path('data/index.faiss')
DOCS_PATH = Path('data/docs.pkl')
DOCS_PATH.mkdir(parents=True, exist_ok=True)
EMBED_DIM = 1536 

class SimpleRAG:
    def __init__(self, embedding_dim=EMBED_DIM):
        self.embedding_dim = embedding_dim
        self.index = None
        self.metadata = []
        if INDEX_PATH.exists():
            self._load()
        else:
            self._init_index()

    def _init_index(self):
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata = []

    def _save(self):
        faiss.write_index(self.index, str(INDEX_PATH))
        with open(str(INDEX_PATH) + '.meta', 'wb') as f:
            pickle.dump(self.metadata, f)

    def _load(self):
        self.index = faiss.read_index(str(INDEX_PATH))
        with open(str(INDEX_PATH) + '.meta', 'rb') as f:
            self.metadata = pickle.load(f)
        self.embedding_dim = self.index.d

    def add(self, embeddings: List[List[float]], metadatas: List[dict]):
        arr = np.array(embeddings).astype('float32')
        if self.index.ntotal == 0 and arr.shape[1] != self.embedding_dim:
            self.embedding_dim = arr.shape[1]
            self._init_index()
        self.index.add(arr)
        self.metadata.extend(metadatas)
        self._save()

    def search(self, embedding: List[float], top_k: int = 4) -> List[Tuple[float, dict]]:
        q = np.array([embedding]).astype('float32')
        if self.index.ntotal == 0:
            return []
        D, I = self.index.search(q, top_k)
        return [(float(D[0][i]), self.metadata[I[0][i]]) for i in range(len(I[0])) if I[0][i] >= 0]

RAG = SimpleRAG()