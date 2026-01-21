"""
Offline Document Ingestion Script

This script demonstrates how document ingestion and vector indexing
can be decoupled from the API service in a production deployment.

In a production environment, this script would:
- Parse documents (text, tables, images)
- Generate embeddings
- Store them in a persistent vector database (e.g., Weaviate)

For local testing and evaluation, ingestion and indexing are performed
at application startup in main.py due to hardware constraints.
"""

from sentence_transformers import SentenceTransformer
import weaviate
import os

WEAVIATE_URL = "http://localhost:8080"
CLASS_NAME = "DocumentChunk"

DATA_DIR = "data"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = weaviate.Client(WEAVIATE_URL)

schema = {
    "class": CLASS_NAME,
    "description": "Chunks of ingested documents (text, tables, image captions)",
    "vectorizer": "none",
    "properties": [
        {
            "name": "content",
            "dataType": ["text"],
            "description": "Document text, table serialization, or image caption"
        },
        {
            "name": "source",
            "dataType": ["text"],
            "description": "Source file name"
        }
    ]
}

if not client.schema.exists(CLASS_NAME):
    client.schema.create_class(schema)

for filename in os.listdir(DATA_DIR):
    file_path = os.path.join(DATA_DIR, filename)

    if not filename.endswith(".txt"):
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    vector = model.encode(content).tolist()

    client.data_object.create(
        data_object={
            "content": content,
            "source": filename
        },
        class_name=CLASS_NAME,
        vector=vector
    )

print("Document ingestion completed successfully.")
