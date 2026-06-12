import PyPDF2
import numpy as np
from sentence_transformers import SentenceTransformer


class RagEngine:
    def __init__(self, pdf_path):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunks = self._load_and_chunk(pdf_path)
        self.embeddings = self.model.encode(self.chunks)

    def _load_and_chunk(self, path):
        reader = PyPDF2.PdfReader(path)
        full_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return [full_text[i:i + 500] for i in range(0, len(full_text), 400)]

    def retrieve(self, query, top_k=3):
        query_emb = self.model.encode([query])
        similarities = np.dot(self.embeddings, query_emb.T).flatten()
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.chunks[i] for i in top_indices]