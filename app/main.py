from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

app = FastAPI(title="Lightweight RAG API")

# -----------------------------
# Load documents at startup
# -----------------------------
documents = []

with open("data/sample.txt", "r", encoding="utf-8") as f:
    documents.append(f.read())

with open("data/image.txt", "r", encoding="utf-8") as f:
    documents.append(f.read())

with open("data/table.txt", "r", encoding="utf-8") as f:
    documents.append(f.read())
# -----------------------------
# Create embeddings (local)
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(documents)

# -----------------------------
# Build FAISS index (in memory)
# -----------------------------
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

@app.get("/")
def home():
    return {"status": "In-memory RAG API running"}

@app.post("/query")
def query_document(question: str):
    query_vector = model.encode([question])
    _, idx = index.search(query_vector, 1)

    answer = documents[idx[0][0]]

    return {
        "question": question,
        "answer": answer
    }
