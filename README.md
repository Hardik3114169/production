# Google Drive Retrieval-Augmented Generation (RAG) System

This repository contains a professional-grade RAG system designed to integrate Google Drive document storage with a localized AI-driven query interface. The system enables automated synchronization, processing, and semantic search over various document formats (PDF, DOCX, TXT).

## Project Objective
Develop a system that integrates with Google Drive to retrieve documents (PDF, Docs, TXT), process and segment the content, generate embeddings, store the information, and enable intelligent question-answering based on that knowledge.

## Directory Structure
```text
reg-gdrive/
├── api/
│   └── main.py          # Backend API services (FastAPI)
├── connectors/
│   ├── gdrive_loader.py # Google Drive API Service Integration
│   └── local_loader.py  # Local Filesystem Data Loader
├── data/
│   └── docs/            # Local cache for synchronized documents
├── embedding/
│   └── embedder.py      # Semantic Vector Generation Logic
├── processing/
│   ├── chunker.py       # Document Segmentation Utilities
│   ├── indexer.py       # Index Orchestration Service
│   └── parser.py        # Document Extraction & Normalization
├── search/
│   └── vector_store.py  # FAISS Vector Database Management
├── run.py               # Command-Line Indexing Interface
└── requirements.txt     # System Dependencies
```

## Component Descriptions
- **API Services**: Built on FastAPI, providing asynchronous endpoints for document synchronization (`/sync-drive`) and natural language querying (`/ask`).
- **Connectors**: Implements the Google Drive API v3 for secure OAuth2-based document retrieval. It supports automated conversion of Google Docs into processable formats.
- **Data Processing**: Includes a robust parsing engine that extracts and normalizes text, followed by a sliding-window chunking strategy to maintain semantic context.
- **Vector Storage**: Utilizes the FAISS library for efficient, high-dimensional similarity searches, allowing the system to identify relevant document segments in milliseconds.

## Technical Stack and Dependencies
- **Core Environment**: Python 3.14
- **Web Framework**: FastAPI (Uvicorn ASGI)
- **Vector Engine**: FAISS (Facebook AI Similarity Search)
- **Document Intelligence**: PyPDF, python-docx
- **Machine Learning Models**:
    - **Embedding Model**: `all-MiniLM-L6-v2` (Sentence-Transformers)
    - **Inference Model**: `MBZUAI/LaMini-Flan-T5-248M` (HuggingFace Transformers)

## Operational Workflow
1. **Data Acquisition**: Documents are retrieved from the Google Drive API and cached locally for processing.
2. **Indexing Pipeline**:
    - Text is extracted and normalized to remove non-standard characters.
    - Data is segmented into 500-character overlapping chunks.
    - Chunks are converted into 384-dimensional vectors via the embedding model.
    - Vectors and associated metadata (Source, Document ID) are committed to the FAISS index.
3. **Query Execution**:
    - User queries are vectorized and compared against the FAISS index.
    - Relevant context is retrieved and passed to the inference model.
    - A grounded response is generated, including citations for all source documents.

## Deployment and Execution
### 1. Environment Setup
Install necessary dependencies within a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration
Place the `credentials.json` (OAuth 2.0 Desktop Client) in the root directory to enable Google Drive API access.

### 3. Execution
To initialize the backend server:
```powershell
uvicorn api.main:app --port 8001
```
The interactive API documentation will be available at `http://127.0.0.1:8001/docs`.

## Key Technical Implementations
- **Asynchronous Task Handling**: Heavy computational tasks (Inference/Indexing) are offloaded to background threads to ensure high API availability.
- **Data Normalization**: Implemented custom regex-based cleaning to ensure optimal tokenization and embedding quality.
- **Metadata Persistence**: Each data chunk is tied to a unique UUID and source tracking, ensuring verifiable AI outputs.

## Limitations and Future Development
- **Compute Requirements**: Local inference requires approximately 2GB of available RAM.
- **Scalability**: Future iterations will include incremental indexing to optimize performance for large-scale repositories.
