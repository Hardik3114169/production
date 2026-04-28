from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import pickle
from embedding.embedder import get_embeddings
from transformers import pipeline
from connectors.gdrive_loader import GDriveLoader
from processing.indexer import index_documents
import os
import asyncio

app = FastAPI()

# Load vector store
with open("vector_store.pkl", "rb") as f:
    store = pickle.load(f)

# Load local LLM
# Using LaMini-Flan-T5 which is tuned for instruction following and better summarization
qa_pipeline = pipeline("text2text-generation", model="MBZUAI/LaMini-Flan-T5-248M")

class Query(BaseModel):
    query: str

class SyncRequest(BaseModel):
    folder_id: str = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Google Drive RAG API", "status": "running"}

@app.post("/sync-drive")
async def sync_drive(req: SyncRequest):
    # Safety check: ignore the placeholder "string" from Swagger
    folder_id = req.folder_id if req.folder_id and req.folder_id != "string" else None
    
    loader = GDriveLoader()
    if not loader.service:
        return {"error": "Google Drive authentication failed or credentials.json missing."}
    
    try:
        # Run GDrive listing and downloading in a separate thread to keep the API responsive
        files = await asyncio.to_thread(loader.list_files, folder_id=folder_id)
        
        downloaded_files = []
        for f in files:
            path = await asyncio.to_thread(loader.download_file, f['id'], f['name'], f['mimeType'])
            if path:
                downloaded_files.append(f['name'])
        
        # Run indexing in a separate thread
        status = await asyncio.to_thread(index_documents)
        
        # Reload the store in memory
        global store
        if os.path.exists("vector_store.pkl"):
            with open("vector_store.pkl", "rb") as f:
                store = pickle.load(f)
                
        return {
            "status": status,
            "files_synced": downloaded_files
        }
    except Exception as e:
        return {"error": f"Sync failed: {str(e)}"}

@app.post("/ask")
async def ask_question(q: Query):
    # Run embedding in a thread
    query_embedding = await asyncio.to_thread(get_embeddings, [q.query])

    # Run search in a thread
    results = await asyncio.to_thread(store.search, query_embedding, k=3)

    context = "\n".join([r["text"] for r in results])

    # Debug logging
    print(f"--- QUERY: {q.query} ---")

    # Run the AI pipeline in a thread (this is the heaviest part)
    prompt = f"Context: {context}\n\nQuestion: {q.query}\n\nAnswer:"
    response = await asyncio.to_thread(qa_pipeline, prompt, max_length=512, do_sample=True, temperature=0.7)
    
    answer = response[0]["generated_text"]
    sources = list(set([r["metadata"]["file_name"] for r in results]))

    return {
        "answer": answer,
        "sources": sources
    }