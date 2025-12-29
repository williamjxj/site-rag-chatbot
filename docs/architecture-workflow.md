# Application Architecture & Workflow

## Complete System Workflow

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
            ChunksTable[(chunks table<br/>- id: String PK<br/>- source: web|file<br/>- uri: String<br/>- title: String<br/>- heading_path: JSON<br/>- text: Text<br/>- text_hash: SHA-256<br/>- embedding: VECTOR 1536<br/>- created_at: DateTime<br/>- updated_at: DateTime)]
            
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

## Detailed Component Structure

```mermaid
graph LR
    subgraph "Project Root"
        Root[site-rag-chatbot/]
    end
    
    subgraph "Frontend - Next.js 14"
        direction TB
        F1[app/<br/>App Router]
        F2[components/<br/>React Components]
        F3[lib/<br/>API Clients & Utils]
        F4[package.json<br/>Tailwind v4<br/>shadcn/ui]
        
        F1 --> F2
        F1 --> F3
        F4 --> F1
    end
    
    subgraph "Backend - FastAPI"
        direction TB
        B1[src/app.py<br/>FastAPI App]
        B2[src/api/routes/<br/>API Endpoints]
        B3[src/ingest/<br/>Ingestion Pipeline]
        B4[src/rag/<br/>RAG Components]
        B5[src/db.py<br/>Database Models]
        B6[src/config.py<br/>Settings]
        
        B1 --> B2
        B1 --> B6
        B2 --> B3
        B2 --> B4
        B3 --> B5
        B4 --> B5
        B5 --> B6
    end
    
    subgraph "Infrastructure"
        I1[docker-compose.yml<br/>PostgreSQL]
        I2[.env<br/>Configuration]
        I3[docs/<br/>Documentation]
    end
    
    Root --> F1
    Root --> B1
    Root --> I1
    Root --> I2
    Root --> I3
```

## Data Flow: Ingestion Workflow

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

## Data Flow: Chat/RAG Workflow

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

## File Structure Overview

```mermaid
graph TD
    Root[site-rag-chatbot/]
    
    Root --> Frontend[frontend/]
    Root --> Backend[backend/]
    Root --> Docs[docs/]
    Root --> ConfigFiles[.gitignore, .markdownlint.json, etc.]
    
    Frontend --> FApp[app/<br/>page.tsx, admin/page.tsx, layout.tsx]
    Frontend --> FComponents[components/<br/>chat/, admin/, ui/]
    Frontend --> FLib[lib/<br/>api/, utils/]
    Frontend --> FConfig[package.json, tailwind.config.ts,<br/>components.json, tsconfig.json]
    
    Backend --> BApp[src/app.py]
    Backend --> BAPI[src/api/routes/<br/>chat.py, ingest.py, admin.py]
    Backend --> BIngest[src/ingest/<br/>pipeline.py, chunking.py,<br/>normalize.py, dedupe.py,<br/>sources/]
    Backend --> BRAG[src/rag/<br/>chat.py, embedder.py,<br/>retriever.py, prompt.py]
    Backend --> BDB[src/db.py]
    Backend --> BConfig[src/config.py]
    Backend --> BDocker[docker-compose.yml]
    Backend --> BReq[requirements.txt, pyproject.toml]
    
    Docs --> DTech[tech-stack-analysis.md]
    Docs --> DImpl[implementation-summary.md]
    Docs --> DQuick[quick-reference.md]
    Docs --> DPlaybook[playbook_*.md]
    
    style Root fill:#f9f9f9
    style Frontend fill:#61dafb
    style Backend fill:#009688
    style Docs fill:#ffd700
```

## Technology Stack Flow

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
