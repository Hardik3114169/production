import faiss
import numpy as np

class VectorStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []
        self.metadata = []

    def add(self, embeddings, texts, metadata):
        self.index.add(np.array(embeddings))
        self.texts.extend(texts)
        self.metadata.extend(metadata)

    def search(self, query_embedding, k=3):
        D, I = self.index.search(query_embedding, k)
        
        results = []
        for i in I[0]:
            results.append({
                "text": self.texts[i],
                "metadata": self.metadata[i]
            })
        return results