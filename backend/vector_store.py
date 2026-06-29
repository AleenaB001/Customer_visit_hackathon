import os
import chromadb
import httpx

from openai import OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.service_now import (
    get_kb_articles,
    get_resolved_incidents
)
from .utils import clean_html

# ============================================================
# OpenAI-Compatible Client (Internal Endpoint)
# ============================================================

http_client = httpx.Client(verify=False)

client = OpenAI(
    base_url="https://genailab.tcs.in",
    api_key="sk-Xnp0YZBIyM-bn3hobXm8EA",
    http_client=http_client
)

EMBEDDING_MODEL = "azure/genailab-maas-text-embedding-3-large"

# ============================================================
# ChromaDB
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chroma_db")

chroma_client = chromadb.PersistentClient(path=DB_PATH)

try:
    kb_collection = chroma_client.get_collection("snow_kb")
except:
    kb_collection = chroma_client.create_collection("snow_kb")

try:
    incident_collection = chroma_client.get_collection("snow_incidents")
except:
    incident_collection = chroma_client.create_collection("snow_incidents")

# ============================================================
# Embedding
# ============================================================

def get_embedding(text):

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding


# ============================================================
# Load KB Articles
# ============================================================

def load_kb():

    docs = []

    for article in get_kb_articles():

        body = f"""
KB Number:
{article.get("number","")}

Title:
{article.get("short_description","")}

Content:
{article.get("text","")}
"""

        body = clean_html(body)

        if body.strip():

            docs.append({
                "id": article["number"],
                "text": body,
                "title": article.get("short_description", "")
            })

    return docs


# ============================================================
# Load Resolved Incidents
# ============================================================

def load_incidents():

    docs = []

    for inc in get_resolved_incidents():

        body = f"""
Incident Number:
{inc.get("number","")}

Category:
{inc.get("category","")}

Priority:
{inc.get("priority","")}

Short Description:
{inc.get("short_description","")}

Description:
{inc.get("description","")}

Resolution:
{inc.get("close_notes","")}

Close Code:
{inc.get("close_code","")}

Assignment Group:
{inc.get("assignment_group","")}
"""

        body = clean_html(body)

        if body.strip():

            docs.append({
                "id": inc["number"],
                "text": body,
                "short_description": inc.get("short_description", ""),
                "category": inc.get("category", ""),
                "priority": inc.get("priority", "")
            })

    return docs


# ============================================================
# Chunk Documents
# ============================================================

def chunk_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = []

    for doc in documents:

        pieces = splitter.split_text(doc["text"])

        for i, piece in enumerate(pieces):

            chunks.append({
                "id": f"{doc['id']}_{i}",
                "text": piece,
                "source_id": doc["id"],
                "title": doc.get("title", ""),
                "short_description": doc.get("short_description", ""),
                "category": doc.get("category", ""),
                "priority": doc.get("priority", "")
            })

    return chunks


# ============================================================
# Build KB Vector Store
# ============================================================

def build_vector_store():

    if kb_collection.count() > 0:
        print("KB Vector Store already exists.")
        return

    docs = load_kb()
    chunks = chunk_documents(docs)

    print(f"Loaded {len(docs)} KB Articles")
    print(f"Created {len(chunks)} KB Chunks")

    for chunk in chunks:

        embedding = get_embedding(chunk["text"])

        kb_collection.add(
            ids=[chunk["id"]],
            documents=[chunk["text"]],
            embeddings=[embedding],
            metadatas=[{
                "kb": chunk["source_id"],
                "title": chunk["title"]
            }]
        )

    print("KB Vector Store Created")


# ============================================================
# Build Incident Vector Store
# ============================================================

def build_incident_vector_store():

    if incident_collection.count() > 0:
        print("Incident Vector Store already exists.")
        return

    docs = load_incidents()
    chunks = chunk_documents(docs)

    print(f"Loaded {len(docs)} Incidents")
    print(f"Created {len(chunks)} Incident Chunks")

    for chunk in chunks:

        embedding = get_embedding(chunk["text"])

        incident_collection.add(
            ids=[chunk["id"]],
            documents=[chunk["text"]],
            embeddings=[embedding],
            metadatas=[{
                "incident": chunk["source_id"],
                "short_description": chunk["short_description"],
                "category": chunk["category"],
                "priority": chunk["priority"]
            }]
        )

    print("Incident Vector Store Created")


# ============================================================
# Search KB
# ============================================================

def search_kb(query, top_k=3):

    embedding = get_embedding(query)

    return kb_collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )


# ============================================================
# Search Incidents
# ============================================================

def search_incidents(query, top_k=3):

    embedding = get_embedding(query)

    return incident_collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )


# ============================================================
# Search Both
# ============================================================

def search(query, top_k=3):

    return {
        "kb": search_kb(query, top_k),
        "incidents": search_incidents(query, top_k)
    }