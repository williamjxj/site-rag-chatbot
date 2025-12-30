# Site RAG Chatbot

A RAG (Retrieval Augmented Generation) chatbot application that ingests content from static websites and documents, and provides a web-based chatbot interface for users to ask questions and receive answers with source citations.

## 🚀 Quick Overview

1. **Upload & Train Documents**: In the `/admin` page, upload documents in various formats (PDF, Markdown, TXT, etc.), then click 'Upload' to automatically process and train the system with your content.

2. **Chat with Your Documents**: From the `/chat` page, you can directly ask questions and chat with the newly uploaded documents. The system uses RAG to provide accurate answers with source citations.

3. **Manage Your Knowledge Base**: Remove documents from the `/admin` page at any time to train and chat with different sets of resources. This allows you to customize your knowledge base for different use cases.

## 🎯 Status

**Core Implementation**: ✅ Complete  
**User Stories**: ✅ All 4 implemented (Chat, Ingestion, Admin, Site Improvements)  
**Tests**: ⏳ Pending (see [Implementation Summary](./docs/implementation-summary.md))

The system is fully functional and ready for use. See [docs/implementation-summary.md](./docs/implementation-summary.md) for detailed implementation documentation.

## Features

- **Chat Interface**: Ask questions and get answers based on ingested content
  - **Markdown Rendering**: Chat responses support rich markdown formatting with syntax highlighting for code blocks
  - **Professional UI**: Branded experience with logo and favicon
- **Content Ingestion**: Ingest content from static websites (via sitemap) and documents (.md, .pdf, .txt)
- **Heading-Aware Chunking**: Markdown files are chunked by semantic sections, preserving document structure
- **Vector Search**: Semantic search using PostgreSQL + pgvector
- **Source Citations**: All answers include source citations
- **Admin Interface**: Manage knowledge base content (view, filter, delete documents)
  - **Organized Layout**: Content organized into tabs (Content Management, Settings, System Status)
  - **Embedding Provider Selection**: Switch between OpenAI and local sentence-transformers embeddings

### Screenshots

<img src="./screenshots/c1.png" style="width: 85%; border: 1px solid #ddd; border-radius: 4px;" alt="Chat Interface" />

<img src="./screenshots/c2.png" style="width: 85%; border: 1px solid #ddd; border-radius: 4px;" alt="Chat with Markdown Rendering" />

<img src="./screenshots/a2.png" style="width: 85%; border: 1px solid #ddd; border-radius: 4px;" alt="Admin Interface - Settings" />

<img src="./screenshots/a1.png" style="width: 85%; border: 1px solid #ddd; border-radius: 4px;" alt="Admin Interface - Content Management" />


## Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, pgvector, OpenAI Embeddings (text-embedding-3-small), Sentence Transformers (local), Deepseek API
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS, shadcn/ui, react-markdown
- **Database**: PostgreSQL 16 with pgvector extension

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- OpenAI API key (for embeddings)
- Deepseek API key (for chat)

### Setup

1. **Start the database**:
   ```bash
   cd backend
   docker compose up -d
   ```

2. **Configure environment**:
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Edit .env with your API keys
   
   # Frontend
   cd ../frontend
   cp .env.example .env.local
   ```

3. **Install dependencies**:
   ```bash
   # Backend
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   
   # Option 1: Install from pyproject.toml (recommended)
   pip install -e .
   
   # Option 2: Install from requirements.txt
   pip install -r requirements.txt
   
   # For development (includes test tools)
   pip install -r requirements-dev.txt
   
   # Frontend
   cd ../frontend
   pnpm install
   ```

4. **Initialize database**:
   ```bash
   cd backend
   python -c "from src.db import init_db; init_db()"
   ```

5. **Start services**:
   ```bash
   # Backend (in one terminal)
   cd backend
   uvicorn src.app:app --reload --port 8000
   
   # Frontend (in another terminal)
   cd frontend
   pnpm run dev
   ```

6. **Ingest content** (optional, for testing):
   ```bash
   cd backend
   python scripts/ingest_once.py
   ```

7. **Open the app**: http://localhost:3000

## Architecture

### System Overview

```mermaid
flowchart TB
    subgraph "User Interface Layer"
        direction TB
        User[User]
        ChatPage["/ - Chat Page<br/>Next.js App Router"]
        AdminPage["/admin - Admin Page<br/>Next.js App Router"]
        
        subgraph "Frontend Components"
            ChatUI[ChatInterface<br/>MessageList, MessageInput<br/>SourceCitations]
            AdminUI[AdminInterface<br/>DocumentList<br/>IngestionStatus<br/>UploadForm]
        end
        
        User --> ChatPage
        User --> AdminPage
        ChatPage --> ChatUI
        AdminPage --> AdminUI
    end
    
    subgraph "API Client Layer"
        direction LR
        ChatAPI[lib/api/chat.ts<br/>POST /chat]
        IngestAPI[lib/api/ingest.ts<br/>POST /ingest]
        AdminAPI[lib/api/admin.ts<br/>GET/DELETE /admin/documents]
        
        ChatUI --> ChatAPI
        AdminUI --> IngestAPI
        AdminUI --> AdminAPI
    end
    
    subgraph "Backend API Layer - FastAPI"
        direction TB
        FastAPI[FastAPI App<br/>Port 8000<br/>CORS Enabled]
        
        subgraph "API Routes"
            ChatRoute["/chat<br/>chat.py"]
            IngestRoute["/ingest<br/>ingest.py"]
            AdminRoute["/admin/documents<br/>admin.py"]
        end
        
        ChatAPI -->|HTTP POST| ChatRoute
        IngestAPI -->|HTTP POST| IngestRoute
        AdminAPI -->|HTTP GET/DELETE| AdminRoute
        
        FastAPI --> ChatRoute
        FastAPI --> IngestRoute
        FastAPI --> AdminRoute
    end
    
    subgraph "RAG Pipeline - Chat Flow"
        direction TB
        ChatHandler[chat.py<br/>answer function]
        Embedder[rag/embedder.py<br/>embed_texts]
        Retriever[rag/retriever.py<br/>retrieve - Vector Search]
        PromptBuilder[rag/prompt.py<br/>build_prompt]
        ChatEngine[rag/chat.py<br/>DeepSeek API Call]
        
        ChatRoute --> ChatHandler
        ChatHandler --> Embedder
        ChatHandler --> Retriever
        ChatHandler --> PromptBuilder
        ChatHandler --> ChatEngine
    end
    
    subgraph "Ingestion Pipeline"
        direction TB
        IngestHandler[ingest.py<br/>ingest_all function]
        
        subgraph "Source Loaders"
            SitemapCrawler[sources/sitemap_crawler.py<br/>fetch_sitemap_urls<br/>fetch_page]
            FileLoader[sources/file_loader.py<br/>iter_files, load_file]
            PDFLoader[sources/pdf_loader.py]
            MDLoader[sources/md_loader.py<br/>extract_headings]
            TXTLoader[sources/file_loader.py]
        end
        
        subgraph "Processing Pipeline"
            Normalizer[normalize.py<br/>normalize_text<br/>Remove boilerplate]
            Chunker[chunking.py<br/>chunk_text<br/>chunk_markdown_by_headings]
            Deduper[dedupe.py<br/>deduplicate_chunks]
            Hasher[chunking.py<br/>hash_text - SHA-256]
        end
        
        IngestRoute --> IngestHandler
        IngestHandler --> SitemapCrawler
        IngestHandler --> FileLoader
        FileLoader --> PDFLoader
        FileLoader --> MDLoader
        FileLoader --> TXTLoader
        
        SitemapCrawler --> Normalizer
        PDFLoader --> Normalizer
        MDLoader --> Normalizer
        TXTLoader --> Normalizer
        
        Normalizer --> Chunker
        Chunker --> Hasher
        Hasher --> Deduper
        Deduper --> Embedder
    end
    
    subgraph "Vector Database Layer"
        direction TB
        DB[(PostgreSQL 16<br/>Docker Container<br/>Port 5432)]
        
        subgraph "Database Schema"
            ChunksTable[(chunks table<br/>- id: String PK<br/>- source: web or file<br/>- uri: String<br/>- title: String<br/>- heading_path: JSON<br/>- text: Text<br/>- text_hash: SHA-256<br/>- embedding: VECTOR 1536<br/>- created_at: DateTime<br/>- updated_at: DateTime)]
            
            VectorIndex[(Vector Index<br/>ivfflat<br/>cosine_ops)]
            SourceIndex[(Source Index)]
            URIIndex[(URI Index)]
            HashIndex[(Hash Index)]
        end
        
        DB --> ChunksTable
        ChunksTable --> VectorIndex
        ChunksTable --> SourceIndex
        ChunksTable --> URIIndex
        ChunksTable --> HashIndex
    end
    
    subgraph "External Services"
        direction LR
        OpenAI[OpenAI API<br/>text-embedding-3-small<br/>1536 dimensions]
        DeepSeek[DeepSeek API<br/>deepseek-chat<br/>Chat Completions]
    end
    
    subgraph "Configuration & Infrastructure"
        direction TB
        Config[config.py<br/>Settings Class<br/>Environment Variables]
        DockerCompose[docker-compose.yml<br/>PostgreSQL + pgvector]
        EnvFile[.env<br/>API Keys<br/>Database URL<br/>Sitemap URL]
    end
    
    %% Data Flow Connections
    Embedder -->|Batch Embeddings| OpenAI
    Embedder -->|Store Embeddings| ChunksTable
    Retriever -->|Vector Similarity Search<br/>cosine_distance<br/>top_k=6| ChunksTable
    ChatEngine -->|POST /v1/chat/completions| DeepSeek
    
    %% Configuration Flow
    Config -->|Reads| EnvFile
    FastAPI -->|Uses| Config
    DB -->|Managed by| DockerCompose
    
    %% Styling
    style User fill:#e1f5ff
    style ChatPage fill:#61dafb
    style AdminPage fill:#61dafb
    style FastAPI fill:#009688
    style DB fill:#336791
    style ChunksTable fill:#4a90e2
    style OpenAI fill:#10a37f
    style DeepSeek fill:#ff6b6b
    style DockerCompose fill:#2496ed
```

### Technology Stack

```mermaid
graph TB
    subgraph "Frontend Stack"
        NextJS[Next.js 14<br/>App Router]
        React[React 18<br/>TypeScript]
        Tailwind[Tailwind CSS v4<br/>@tailwindcss/postcss]
        Shadcn[shadcn/ui<br/>Radix UI]
        NextJS --> React
        NextJS --> Tailwind
        NextJS --> Shadcn
    end
    
    subgraph "Backend Stack"
        FastAPI[FastAPI<br/>Python 3.10+]
        SQLAlchemy[SQLAlchemy 2.0<br/>ORM]
        Pydantic[Pydantic 2.0<br/>Validation]
        FastAPI --> SQLAlchemy
        FastAPI --> Pydantic
    end
    
    subgraph "Database Stack"
        PostgreSQL[PostgreSQL 16]
        PgVector[pgvector Extension<br/>Vector Similarity]
        PostgreSQL --> PgVector
    end
    
    subgraph "AI/ML Stack"
        OpenAI[OpenAI API<br/>Embeddings<br/>text-embedding-3-small]
        DeepSeek[DeepSeek API<br/>Chat Completions<br/>deepseek-chat]
    end
    
    NextJS -->|HTTP REST| FastAPI
    SQLAlchemy -->|SQL| PostgreSQL
    FastAPI -->|API Calls| OpenAI
    FastAPI -->|API Calls| DeepSeek
    
    style NextJS fill:#000000,color:#fff
    style FastAPI fill:#009688,color:#fff
    style PostgreSQL fill:#336791,color:#fff
    style OpenAI fill:#10a37f,color:#fff
    style DeepSeek fill:#ff6b6b,color:#fff
```

## Project Structure

```
site-rag-chatbot/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── app.py             # FastAPI application
│   │   ├── config.py          # Configuration
│   │   ├── db.py              # Database models
│   │   ├── ingest/            # Ingestion pipeline
│   │   │   ├── pipeline.py
│   │   │   ├── chunking.py
│   │   │   └── sources/       # File loaders
│   │   ├── rag/               # RAG components
│   │   │   ├── embedder.py
│   │   │   ├── retriever.py
│   │   │   └── chat.py
│   │   └── api/               # API routes
│   ├── tests/                 # Tests (pending)
│   ├── scripts/
│   │   └── ingest_once.py
│   ├── pyproject.toml
│   └── docker-compose.yml
├── frontend/                   # Next.js frontend
│   ├── app/                   # Next.js App Router
│   │   ├── page.tsx            # Chat interface
│   │   └── admin/
│   │       └── page.tsx        # Admin interface
│   ├── components/
│   │   ├── chat/              # Chat components
│   │   └── admin/             # Admin components
│   ├── lib/
│   │   ├── api/               # API clients
│   │   └── utils/              # Utilities
│   └── package.json
├── docs/
│   ├── implementation-summary.md  # Detailed implementation docs
│   ├── chatgpt.md             # Original blueprint
└   └── variable.md            # Technology decisions
```

## API Endpoints

- `POST /chat` - Ask a question and get an answer
- `POST /ingest` - Trigger content ingestion
- `GET /admin/documents` - List ingested documents (with optional source filter)
- `DELETE /admin/documents/{id}` - Remove a document
- `GET /admin/config/embedding-provider` - Get current embedding provider configuration
- `PUT /admin/config/embedding-provider` - Update embedding provider preference


## Usage

### Chat Interface

1. Open http://localhost:3000
2. Type a question in the chat interface
3. Receive answers with source citations

### Admin Interface

1. Open http://localhost:3000/admin
2. **Content Management Tab**:
   - **Upload Documents**: Upload PDF, Markdown, or text files
   - **Manage Documents**: View, filter, and delete documents from the knowledge base
3. **Settings Tab**:
   - **Embedding Provider**: Select between OpenAI (text-embedding-3-small) or local sentence-transformers
   - Changes take effect on the next ingestion operation (no restart required)
4. **System Status Tab**:
   - **Ingest Content**: Click "Ingest All" to crawl website and process documents
   - Monitor ingestion status and progress

### Data Flow

#### Chat/RAG Workflow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Next.js Frontend
    participant API as FastAPI /chat
    participant Embedder as Embedder
    participant Retriever as Retriever
    participant DB as PostgreSQL + pgvector
    participant OpenAI as OpenAI API
    participant Prompt as Prompt Builder
    participant DeepSeek as DeepSeek API
    
    User->>Frontend: Type question
    Frontend->>API: POST /chat {question: "..."}
    
    API->>Embedder: embed_texts([question])
    Embedder->>OpenAI: POST /embeddings<br/>{model: "text-embedding-3-small"}
    OpenAI-->>Embedder: {data: [{embedding: [1536 floats]}]}
    Embedder-->>API: query_embedding [1536-dim vector]
    
    API->>Retriever: retrieve(query_embedding, top_k=6)
    Retriever->>DB: SELECT * FROM chunks<br/>ORDER BY cosine_distance(embedding, ?)<br/>LIMIT 6
    DB-->>Retriever: [Chunk objects]
    Retriever-->>API: [top-k chunks]
    
    API->>API: Build context blocks<br/>(max 12000 chars)
    
    API->>Prompt: build_prompt(question, context)
    Prompt-->>API: Formatted prompt with context
    
    API->>DeepSeek: POST /v1/chat/completions<br/>{model: "deepseek-chat",<br/>messages: [system, user]}
    DeepSeek-->>API: {choices: [{message: {content: "answer"}}]}
    
    API->>API: Extract sources from chunks
    API-->>Frontend: {answer: "...", sources: [...]}
    Frontend->>User: Display answer + citations
```

#### Ingestion Workflow

```mermaid
sequenceDiagram
    participant Admin as Admin UI
    participant API as FastAPI /ingest
    participant Pipeline as Ingestion Pipeline
    participant Loader as Source Loaders
    participant Processor as Text Processor
    participant Embedder as Embedder
    participant DB as PostgreSQL
    
    Admin->>API: POST /ingest {source: "all"}
    API->>Pipeline: ingest_all()
    
    alt Website Source
        Pipeline->>Loader: fetch_sitemap_urls()
        Loader-->>Pipeline: List of URLs
        loop For each URL
            Pipeline->>Loader: fetch_page(url)
            Loader-->>Pipeline: {title, text}
        end
    else File Source
        Pipeline->>Loader: iter_files(docs_dir)
        Loader-->>Pipeline: List of file paths
        loop For each file
            alt PDF
                Pipeline->>Loader: load_file(pdf)
            else Markdown
                Pipeline->>Loader: load_file(md)
                Note over Loader: Extract headings
            else Text
                Pipeline->>Loader: load_file(txt)
            end
            Loader-->>Pipeline: {uri, title, text}
        end
    end
    
    Pipeline->>Processor: normalize_text()
    Processor-->>Pipeline: Cleaned text
    
    alt Markdown with headings
        Pipeline->>Processor: chunk_markdown_by_headings()
        Processor-->>Pipeline: [(text, heading_path)]
    else Other files
        Pipeline->>Processor: chunk_text()
        Processor-->>Pipeline: [text chunks]
    end
    
    Pipeline->>Processor: hash_text()
    Processor-->>Pipeline: SHA-256 hash
    
    Pipeline->>Processor: deduplicate_chunks()
    Processor-->>Pipeline: Deduplicated chunks
    
    Pipeline->>Embedder: embed_texts([texts])
    Embedder->>Embedder: Batch API call
    Embedder-->>Pipeline: [embeddings 1536-dim]
    
    loop For each chunk
        Pipeline->>DB: UPSERT chunk
        Note over DB: Check hash, update if changed<br/>Insert if new
    end
    
    DB-->>Pipeline: Success
    Pipeline-->>API: {web_chunks, file_chunks}
    API-->>Admin: IngestResponse
```

### Configuration

Edit `backend/.env`:
- `SITEMAP_URL`: URL to your website's sitemap.xml
- `DOCS_DIR`: Path to directory containing .md, .pdf, .txt files
- `LLM_PROVIDER`: Provider name (e.g., "deepseek" or "openai")
- `OPENAI_BASE_URL`: Base URL for OpenAI-compatible API (e.g., "https://api.deepseek.com")
- `OPENAI_API_KEY`: Your API key for embeddings and chat
- `VECTOR_STORE`: Vector store type ("memory" for dev, "pgvector" for production)
- `EMBEDDING_PROVIDER`: Embedding provider ("openai" for text-embedding-3-small, "local" for sentence-transformers, or "" for auto-detect)
  - Can be updated via the admin interface (Settings tab) without restarting the backend

## Backend Dependencies

The backend uses **pyproject.toml** (modern Python standard) for dependency management. For convenience, `requirements.txt` files are also provided.

**View dependencies:**
- `backend/pyproject.toml` - Source of truth
- `backend/requirements.txt` - Production dependencies
- `backend/requirements-dev.txt` - Development dependencies (includes test tools)

**Install:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .  # Or: pip install -r requirements.txt
```

See [backend/README.md](./backend/README.md) for more details.

## Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
pnpm test
pnpm run test:e2e
```

### Code Quality

```bash
# Backend
cd backend
ruff check .
black .
mypy src/

# Frontend
cd frontend
pnpm run lint
```

## Documentation

- **[Implementation Summary](./docs/implementation-summary.md)** - Detailed implementation documentation, architecture, design decisions, and future enhancements
- **[Site Improvements](./docs/004-site-improvements.md)** - Documentation for UI improvements and embedding provider selection
- **[API Contract](./specs/001-rag-chatbot/contracts/api.yaml)** - OpenAPI specification (core features)
- **[API Contract (Site Improvements)](./specs/004-site-improvements/contracts/api.yaml)** - OpenAPI specification (embedding provider config)
- **[Feature Specification](./specs/001-rag-chatbot/spec.md)** - Original feature requirements
- **[Site Improvements Specification](./specs/004-site-improvements/spec.md)** - Site improvements feature requirements
- **[Quickstart Guide](./specs/001-rag-chatbot/quickstart.md)** - Step-by-step setup instructions

## Implementation Details

### Completed Features

✅ **User Story 1 - Chat Interface**
- RAG pipeline (embedding, retrieval, generation)
- Chat UI with message history
- Source citations
- Loading states and error handling

✅ **User Story 2 - Content Ingestion**
- Website crawling via sitemap
- File loaders (PDF, Markdown, TXT)
- Heading-aware chunking for markdown files
- Chunking and embedding pipeline
- Incremental updates with change detection

✅ **User Story 3 - Admin Interface**
- Document listing with filtering
- Document deletion
- Ingestion controls
- Organized tabbed interface (Content Management, Settings, System Status)

✅ **User Story 4 - Site Improvements**
- Logo and favicon for branded experience
- Markdown rendering in chat responses with syntax highlighting
- Admin page reorganization with shadcn/ui tabs
- Embedding provider selection (OpenAI or local sentence-transformers)

### Pending Work

- Comprehensive test suite (unit, integration, E2E)
- Performance optimizations (caching, query optimization)
- File upload handler (multipart/form-data)
- Additional polish and enhancements

See [Implementation Summary](./docs/implementation-summary.md) for complete details.

## Troubleshooting

### Database Connection Issues

If you see `psycopg.OperationalError: connection refused`:
```bash
cd backend
docker compose ps  # Check if database is running
docker compose restart  # Restart if needed
```

### API Key Errors

Ensure your `backend/.env` file has valid API keys:
- `OPENAI_API_KEY` - Required for embeddings and chat (if using OpenAI-compatible provider)
- `OPENAI_BASE_URL` - Set to provider's base URL (e.g., "https://api.deepseek.com" for DeepSeek)
- `LLM_PROVIDER` - Set to "deepseek" or "openai" (defaults to "openai")

### No Answers Returned

1. Verify content has been ingested: Check `/admin/documents` endpoint
2. Ensure questions relate to ingested content
3. Check backend logs for embedding/retrieval errors

## Contributing

This is a feature implementation following the `/speckit` workflow. See `specs/001-rag-chatbot/` for specifications and design documents.

## License

MIT
