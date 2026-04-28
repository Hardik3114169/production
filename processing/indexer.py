import os
import uuid
import pickle
from processing.parser import parse_file
from processing.chunker import chunk_text
from embedding.embedder import get_embeddings
from search.vector_store import VectorStore

def index_documents(folder_path="data/docs", vector_store_path="vector_store.pkl", source="gdrive"):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
             if f.endswith((".pdf", ".docx", ".txt"))]
    
    all_chunks = []
    all_metadata = []
    
    for file in files:
        try:
            text = parse_file(file)
            if not text:
                continue
                
            chunks = chunk_text(text)
            doc_id = str(uuid.uuid4())
            
            for chunk in chunks:
                all_chunks.append(chunk)
                all_metadata.append({
                    "doc_id": doc_id,
                    "file_name": os.path.basename(file),
                    "source": source
                })
        except Exception as e:
            print(f"Error processing {file}: {e}")

    if not all_chunks:
        return "No documents found to index."

    embeddings = get_embeddings(all_chunks)
    store = VectorStore(len(embeddings[0]))
    store.add(embeddings, all_chunks, all_metadata)

    with open(vector_store_path, "wb") as f:
        pickle.dump(store, f)
        
    return f"Indexed {len(files)} files successfully."
