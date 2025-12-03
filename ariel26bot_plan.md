# Development Plan: Ariel CS 2026 Telegram Bot

## Overview

This plan outlines the complete implementation roadmap for building a production-ready AI-powered Telegram bot for Computer Science students at Ariel University. The bot will provide RAG-based Q&A using course materials, vision-based problem solving, and password-protected access.

**Current State**: Greenfield project (only product_overview.md exists)
**Target**: Full MVP deployed to Google Cloud Platform
**Timeline**: 6-8 weeks
**Key Technologies**: Python, Telegram Bot API, Google Gemini 1.5 Flash, Google File Search, GCP Cloud Run, Firestore

---

## Technology Stack

### Core Framework
- **Python**: 3.10+ (required for modern async features)
- **Bot Framework**: `python-telegram-bot` v22.3+
  - Rationale: Excellent documentation, beginner-friendly, fully async, stable production library
- **Web Framework**: FastAPI + Uvicorn (for webhook mode in production)

### AI & RAG
- **LLM**: Google Gemini 1.5 Flash via `google-genai` SDK
- **Vector Store**: Google File Search (managed, no separate DB needed)
- **Context Window**: 1M tokens (excellent for complex queries)

### Cloud Infrastructure (GCP)
- **Compute**: Cloud Run (serverless containers, auto-scaling)
- **Database**: Firestore (user allowlist, session state)
- **Secrets**: Secret Manager (API keys, passwords)
- **Logging**: Cloud Logging & Monitoring

### Key Dependencies
```
python-telegram-bot==22.3
google-genai==1.8.0
fastapi==0.115.0
uvicorn[standard]==0.32.0
google-cloud-firestore==2.20.0
google-cloud-secret-manager==2.21.0
pydantic==2.10.0
pydantic-settings==2.6.0
pillow==11.0.0
structlog==25.1.0
pytest==8.3.0
pytest-asyncio==0.25.0
```

---

## Project Structure

Using **src layout** (Python best practice for installable packages):

```
ArielCS26bot/
├── src/ariel_bot/
│   ├── __init__.py
│   ├── main.py                      # FastAPI webhook server + entry point
│   ├── config.py                    # Pydantic settings management
│   ├── bot/
│   │   ├── application.py           # Bot setup and handler registration
│   │   ├── handlers/                # Command and message handlers
│   │   │   ├── start.py            # /start, /help
│   │   │   ├── auth.py             # Password verification flow
│   │   │   ├── question.py         # Text Q&A handler
│   │   │   └── vision.py           # Image upload handler
│   │   ├── middleware/
│   │   │   ├── auth_middleware.py  # Auth check before processing
│   │   │   └── logging_middleware.py
│   │   └── keyboards.py             # Telegram keyboards/buttons
│   ├── rag/
│   │   ├── file_search.py           # Google File Search integration
│   │   ├── document_processor.py    # Document scanning/upload utilities
│   │   └── citation_formatter.py    # Format citation references
│   ├── vision/
│   │   ├── image_processor.py       # Download/validate images
│   │   ├── ocr_service.py          # Gemini Vision API integration
│   │   └── latex_formatter.py       # LaTeX formatting
│   ├── auth/
│   │   ├── password_manager.py      # Password verification
│   │   └── allowlist.py            # Firestore user management
│   ├── storage/
│   │   └── user_repository.py       # User data operations
│   └── utils/
│       ├── logger.py               # Structured logging (structlog)
│       ├── exceptions.py           # Custom exceptions
│       └── rate_limiter.py         # Rate limiting logic
├── scripts/
│   ├── create_vector_store.py       # Initialize File Search store
│   ├── upload_documents.py          # Upload course materials
│   └── test_gemini_connection.py    # Verify API connectivity
├── tests/
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── fixtures/                    # Test data
├── docs/
│   ├── setup.md                     # Local development setup
│   ├── deployment.md                # Cloud deployment guide
│   └── api_keys.md                  # How to obtain API keys
├── data/course_materials/           # Local storage for documents
│   ├── intro_to_cs/
│   ├── calculus_1/
│   └── linear_algebra/
├── .env.example                     # Environment variable template
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies
├── Dockerfile                       # Container definition
├── README.md
└── product_overview.md
```

---

## Implementation Phases

### Phase 1: Foundation & Environment Setup (Week 1)

**Goal**: Development environment ready, all APIs tested

**Tasks**:
1. Create project directory structure (src layout)
2. Set up Python virtual environment
3. Create `.gitignore`, `.env.example`, `requirements.txt`
4. Obtain API credentials:
   - Telegram Bot Token (via @BotFather)
   - Google Gemini API Key (AI Studio)
   - GCP Project ID and enable APIs (Gemini, Firestore, Secret Manager, Cloud Run)
5. Initialize Firestore database (Native mode)
6. Create basic configuration management (`config.py` with pydantic-settings)
7. Set up structured logging (`utils/logger.py`)
8. Create minimal bot with `/start` command
9. Test all API connections with scripts

**Testing**: Manual - bot responds to /start, scripts verify Gemini and Firestore connectivity

**Deliverables**: Working dev environment, all APIs verified, bot responds to basic commands

---

### Phase 2: Authentication System (Week 2)

**Goal**: Password-based access control with persistent user allowlist

**User Flow**:
```
User sends /start
  → Check if user_id in Firestore allowlist
  → If NOT authorized: Prompt for password
      → Verify password
      → If CORRECT: Add to allowlist, grant access
      → If INCORRECT: Deny access
  → If authorized: Welcome back message
```

**Tasks**:
1. Create `auth/password_manager.py` - password verification logic
2. Create `auth/allowlist.py` - Firestore CRUD operations for user management
3. Create `handlers/auth.py` - ConversationHandler for password flow
4. Create `middleware/auth_middleware.py` - block unauthorized users
5. Update `handlers/start.py` - integrate auth flow
6. Store user metadata (user_id, username, added_at, last_active)

**Testing**:
- Unit tests: Password verification, Firestore operations
- Integration: Full auth flow with multiple users
- Manual: Test wrong passwords, existing users

**Deliverables**: Working password gate, persistent allowlist in Firestore

---

### Phase 3: RAG System - Document Ingestion (Week 3)

**Goal**: Upload course materials to Google File Search vector store

**Tasks**:
1. Organize course materials in `data/course_materials/` by course
2. Create `scripts/create_vector_store.py`:
   - Initialize File Search store via Gemini API
   - Display name: "Ariel CS 2026 Knowledge Base"
   - Save vector_store_id to .env
3. Create `scripts/upload_documents.py`:
   - Scan directories for PDFs, DOCX, TXT, MD files
   - Upload to File Search with metadata (course, topic)
   - Display progress bar
4. Create `rag/document_processor.py` - reusable upload utilities
5. Test retrieval with direct Gemini API queries

**File Search Setup Example**:
```python
from google import genai

client = genai.Client(api_key=GEMINI_API_KEY)

# Create vector store
vector_store = client.files.create_vector_store(
    display_name="Ariel CS 2026 Knowledge Base"
)

# Upload document
file = client.files.upload(
    path="data/course_materials/calculus_1/lecture_05.pdf",
    display_name="Calculus 1 - Lecture 5"
)

# Add to vector store
client.files.add_to_vector_store(
    vector_store_id=vector_store.id,
    file_id=file.id
)
```

**Testing**: Verify files appear in Google AI Studio, test search queries

**Deliverables**: Vector store populated with course materials, reusable upload scripts

---

### Phase 4: RAG System - Q&A Handler (Week 3-4)

**Goal**: Implement text-based Q&A using File Search with citations

**Tasks**:
1. Create `rag/file_search.py`:
   - Query File Search with user questions
   - Configure Gemini with File Search tool
   - Extract grounding metadata (citations)
2. Create `rag/citation_formatter.py`:
   - Parse grounding chunks
   - Format user-friendly citations (e.g., "Source: Lecture 5, page 3")
3. Create `handlers/question.py`:
   - Accept text messages as questions
   - Call RAG service
   - Return answer with formatted citations
   - Handle "no relevant info" cases gracefully
4. Add typing indicators for better UX

**RAG Query Pattern**:
```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=question,
    config={
        "tools": [{
            "file_search": {
                "vector_store_ids": [vector_store_id]
            }
        }],
        "temperature": 0.3  # Lower for factual responses
    }
)

answer = response.text
citations = extract_citations(response.grounding_metadata)
```

**Testing**:
- Unit: Citation formatting
- Integration: End-to-end RAG query
- Manual: Various questions (factual, conceptual, out-of-scope)

**Deliverables**: Working Q&A system with source citations

---

### Phase 5: Vision System - "Snap & Solve" (Week 5)

**Goal**: Image-based problem solving with OCR → LaTeX → Explanation

**Processing Flow**:
```
User uploads image
  → Download image from Telegram
  → Validate and compress if needed
  → Gemini Vision: Extract problem → LaTeX
  → Query RAG with extracted problem
  → Generate step-by-step solution
  → Return: LaTeX + explanation + citations
```

**Tasks**:
1. Create `vision/image_processor.py`:
   - Download images from Telegram
   - Validate format and size
   - Compress if > 5MB or dimensions > 2048px
2. Create `vision/ocr_service.py`:
   - Use Gemini 1.5 Flash Vision
   - Prompt: "Extract mathematical problem, convert to LaTeX"
   - Parse response (LaTeX, problem type, context)
3. Create `vision/latex_formatter.py` - format for Telegram display
4. Create `handlers/vision.py`:
   - Handle PHOTO messages
   - Integrate vision + RAG pipeline
   - Send formatted response
5. Implement cleanup of temporary image files

**Gemini Vision Example**:
```python
# Upload image
uploaded_file = client.files.upload(path=image_path)

# Analyze with vision
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        uploaded_file,
        "Extract the mathematical problem from this image. "
        "Convert handwritten math to LaTeX format."
    ]
)
```

**Testing**:
- Unit: Image validation, LaTeX parsing
- Integration: Full vision pipeline
- Manual: Various handwriting styles, different problem types

**Deliverables**: Working image-to-solution pipeline

---

### Phase 6: Polish & Production Readiness (Week 6)

**Goal**: Error handling, logging, rate limiting, user experience

**Tasks**:
1. Implement comprehensive error handling:
   - Custom exceptions (`utils/exceptions.py`)
   - Global error handler for bot
   - User-friendly error messages
   - Retry logic for API failures
2. Enhance logging:
   - Structured JSON logging with structlog
   - Log all user interactions, API calls, errors
   - Integration with Cloud Logging
3. Implement rate limiting (`utils/rate_limiter.py`):
   - Token bucket algorithm
   - Limits: 50 questions/hour, 10 vision queries/hour per user
   - Graceful rejection messages
4. Create `/help` command with feature overview
5. Add inline keyboards for common actions (optional)
6. Performance optimization:
   - Async image processing
   - Concurrent API calls where possible

**Testing**:
- Unit: Rate limiter logic
- Integration: Error scenarios (API timeout, invalid key)
- Load: Simulate concurrent users

**Deliverables**: Robust, production-ready bot with proper error handling

---

### Phase 7: Cloud Deployment (Week 7)

**Goal**: Deploy to GCP Cloud Run with webhook mode

**Architecture**:
```
Telegram → Webhook → Cloud Run (FastAPI) → Bot Handlers
                            ↓
                    Gemini API (File Search)
                    Firestore (Users)
                    Secret Manager (Keys)
```

**Tasks**:
1. Create `Dockerfile`:
   - Multi-stage build (reduce image size)
   - Non-root user for security
   - Health check endpoint
2. Create FastAPI webhook server in `main.py`:
   - POST /webhook endpoint
   - GET /health endpoint
   - Integrate with python-telegram-bot Application
3. Set up Secret Manager:
   - Store TELEGRAM_TOKEN, GEMINI_API_KEY, BOT_PASSWORD
   - Update config.py to fetch from Secret Manager in prod
4. Deploy to Cloud Run:
   - Build and push container to GCR
   - Configure environment variables
   - Set autoscaling (min=0, max=10)
   - Allocate 1 CPU, 512MB RAM
5. Set Telegram webhook to Cloud Run URL
6. Configure Cloud Logging and Monitoring
7. Set up billing alerts

**Deployment Commands**:
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/ariel-bot

# Deploy to Cloud Run
gcloud run deploy ariel-bot \
  --image gcr.io/PROJECT_ID/ariel-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets TELEGRAM_TOKEN=telegram-token:latest

# Set webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://ariel-bot-xxx.run.app/webhook"
```

**Testing**:
- Local: Test Docker container
- Staging: Deploy to test Cloud Run service
- Production: Smoke tests after deployment

**Deliverables**: Bot running on Cloud Run, webhook active, monitoring enabled

---

### Phase 8: Testing & Documentation (Week 8)

**Goal**: Comprehensive testing and user/developer documentation

**Tasks**:
1. Write unit tests (target 80% coverage):
   - Auth logic, RAG formatting, citation extraction
   - Vision processing, rate limiting
   - Run with pytest and coverage report
2. Write integration tests:
   - Full conversation flows
   - Mock API integrations
3. Manual testing checklist:
   - New user onboarding
   - Q&A scenarios (factual, out-of-scope, nonsense)
   - Vision uploads (clear, blurry, non-math)
   - Rate limiting edge cases
   - Error scenarios
4. Create documentation:
   - `README.md`: Project overview, quick start
   - `docs/setup.md`: Local development setup
   - `docs/deployment.md`: Cloud deployment guide
   - `docs/api_keys.md`: How to obtain credentials
5. Code review and refactoring

**Testing Strategy**:
```bash
# Unit tests
pytest tests/unit/ -v --cov=src/ariel_bot --cov-report=html

# Integration tests
pytest tests/integration/ -v
```

**Deliverables**: Test suite, complete documentation, production-ready codebase

---

## Core Component Design

### 1. Configuration Management

**File**: `src/ariel_bot/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = False

    # Telegram
    telegram_token: str
    webhook_url: str | None = None

    # Google AI
    gemini_api_key: str
    vector_store_id: str
    gemini_model: str = "gemini-2.5-flash"

    # GCP
    gcp_project_id: str

    # Security
    bot_password: str

    # Rate Limiting
    max_questions_per_hour: int = 50
    max_vision_per_hour: int = 10

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### 2. Bot Application Setup

**File**: `src/ariel_bot/bot/application.py`

```python
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters
from .handlers import start, auth, question, vision
from .middleware import auth_middleware

def create_application() -> Application:
    app = Application.builder().token(settings.telegram_token).build()

    # Middleware
    app.add_handler(auth_middleware, group=-1)

    # Auth conversation
    auth_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start.start_command)],
        states={
            auth.AWAITING_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, auth.verify_password)
            ]
        },
        fallbacks=[CommandHandler("cancel", start.cancel)]
    )
    app.add_handler(auth_conv)

    # Handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, question.handle_question))
    app.add_handler(MessageHandler(filters.PHOTO, vision.handle_image))
    app.add_handler(CommandHandler("help", start.help_command))

    # Error handler
    app.add_error_handler(error_handler)

    return app
```

### 3. RAG Query Service

**File**: `src/ariel_bot/rag/file_search.py`

```python
from google import genai

client = genai.Client(api_key=settings.gemini_api_key)

async def query_knowledge_base(question: str, vector_store_id: str) -> dict:
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=question,
        config={
            "tools": [{
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }],
            "temperature": 0.3,
            "top_p": 0.95
        }
    )

    citations = extract_citations(response.grounding_metadata)

    return {
        "answer": response.text,
        "citations": citations
    }

def extract_citations(grounding_metadata) -> list:
    citations = []
    if grounding_metadata:
        for chunk in grounding_metadata.get("grounding_chunks", []):
            citations.append({
                "display_name": chunk.get("display_name"),
                "page": chunk.get("page_number")
            })
    return list({c["display_name"]: c for c in citations}.values())
```

### 4. Authentication Flow

**File**: `src/ariel_bot/auth/allowlist.py`

```python
from google.cloud import firestore
from datetime import datetime

db = firestore.AsyncClient(project=settings.gcp_project_id)

async def is_user_authorized(user_id: int) -> bool:
    doc = await db.collection("users").document(str(user_id)).get()
    if doc.exists:
        return doc.to_dict().get("authorized", False)
    return False

async def add_user_to_allowlist(user_id: int, username: str = None, full_name: str = None):
    await db.collection("users").document(str(user_id)).set({
        "user_id": user_id,
        "username": username,
        "full_name": full_name,
        "authorized": True,
        "added_at": datetime.utcnow(),
        "last_active": datetime.utcnow()
    })
```

### 5. Vision Processing

**File**: `src/ariel_bot/vision/ocr_service.py`

```python
from google import genai
from pathlib import Path

class OCRService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)

    async def extract_math_problem(self, image_path: Path) -> dict:
        uploaded_file = self.client.files.upload(path=str(image_path))

        prompt = """
        Extract the mathematical problem from this image:
        1. Convert handwritten/printed math to LaTeX
        2. Identify problem type (calculus, algebra, etc.)
        3. Extract any text instructions

        Format: LATEX: [...] TYPE: [...] CONTEXT: [...]
        """

        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=[uploaded_file, prompt]
        )

        return self._parse_response(response.text)
```

### 6. Rate Limiting

**File**: `src/ariel_bot/utils/rate_limiter.py`

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int, time_window: timedelta):
        self.max_requests = max_requests
        self.time_window = time_window
        self.user_requests = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        now = datetime.utcnow()
        cutoff = now - self.time_window

        # Remove old timestamps
        self.user_requests[user_id] = [
            ts for ts in self.user_requests[user_id] if ts > cutoff
        ]

        # Check limit
        if len(self.user_requests[user_id]) >= self.max_requests:
            return False

        # Allow and record
        self.user_requests[user_id].append(now)
        return True
```

### 7. Webhook Server

**File**: `src/ariel_bot/main.py`

```python
from fastapi import FastAPI, Request
from telegram import Update
from .bot.application import create_application

app = FastAPI()
bot_app = create_application()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

## Security Best Practices

### API Key Management

**Development** (.env):
```bash
TELEGRAM_TOKEN=123456:ABC...
GEMINI_API_KEY=AIzaSy...
BOT_PASSWORD=SecurePass123
```

**Production** (Secret Manager):
```bash
# Create secrets
gcloud secrets create telegram-token --data-file=token.txt
gcloud secrets create gemini-api-key --data-file=key.txt

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding telegram-token \
  --member="serviceAccount:PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Error Handling

- Custom exceptions for different error types
- Global error handler in bot application
- User-friendly error messages (never expose internals)
- Retry logic with exponential backoff for API calls
- Structured logging for debugging

### Rate Limiting

- Per-user limits: 50 questions/hour, 10 vision/hour
- Token bucket algorithm
- Clear messaging when limit exceeded
- Reset time indication

---

## Data Management

### Course Materials Organization

```
data/course_materials/
├── intro_to_cs/
│   ├── syllabus.pdf
│   ├── lecture_01_introduction.pdf
│   ├── exercises_week1.pdf
│   └── past_exam_2023.pdf
├── calculus_1/
│   ├── syllabus.pdf
│   ├── lecture_01_limits.pdf
│   └── summary_limits.md
└── linear_algebra/
    ├── syllabus.pdf
    └── lecture_01_vectors.pdf
```

**Naming Convention**: `lecture_NN_topic.pdf`, `exercises_topic.pdf`

### Firestore Collections

**users** collection:
```json
{
  "user_id": 123456789,
  "username": "dan_student",
  "full_name": "Dan Cohen",
  "authorized": true,
  "added_at": "2025-12-01T10:30:00Z",
  "last_active": "2025-12-02T15:45:00Z",
  "queries_count": 42,
  "vision_queries_count": 5
}
```

---

## Cloud Deployment

### Platform: Google Cloud Platform (GCP)

**Why GCP**:
- Native Gemini integration (same account)
- Generous free tier
- Serverless options (Cloud Run, Firestore)
- Best for AI workloads with Google services

### Architecture

```
Telegram Users
    ↓
Telegram API (Webhook)
    ↓
Cloud Run (FastAPI + Bot)
    ↓
├── Firestore (Users)
├── Gemini API (Text + Vision)
│   └── File Search (Vector Store)
└── Secret Manager (Credentials)
```

### Cost Estimate

**Monthly costs** (500 active students):
- Cloud Run: ~FREE (within free tier)
- Firestore: ~FREE (within free tier)
- Gemini API: $15-40 (depends on usage)
- File Search: $1-5 one-time upload cost
- **Total: $15-40/month**

### Scaling Strategy

- **MVP (0-100 users)**: 0-2 Cloud Run instances, 1 CPU, 512MB RAM
- **Growth (100-500 users)**: 0-5 instances, 1 CPU, 1GB RAM, consider caching
- **Scale (500+ users)**: 1-10 instances (min 1), 2 CPU, 2GB RAM, implement query caching

---

## Testing Strategy

### Unit Tests
- Auth: Password verification, allowlist operations
- RAG: Citation extraction, query formatting
- Vision: Image validation, LaTeX parsing
- Rate Limiter: Token bucket logic

### Integration Tests
- Full conversation flows (auth → question → answer)
- API integrations (mocked for reliability)
- Error scenarios (timeouts, invalid keys)

### Manual Testing Checklist
- [ ] New user flow (wrong password, correct password)
- [ ] Q&A scenarios (factual, out-of-scope, nonsense)
- [ ] Vision uploads (clear, blurry, non-math image)
- [ ] Rate limiting (exceed limits, reset)
- [ ] Error handling (API failures, invalid input)

---

## Critical Files to Create

### Phase 1 (Foundation)
1. `.gitignore` - Ignore venv, .env, __pycache__
2. `.env.example` - Environment variable template
3. `requirements.txt` - Production dependencies
4. `requirements-dev.txt` - Development dependencies
5. `pyproject.toml` - Project metadata
6. `src/ariel_bot/config.py` - Configuration management
7. `src/ariel_bot/main.py` - Entry point
8. `src/ariel_bot/utils/logger.py` - Structured logging
9. `scripts/test_gemini_connection.py` - API verification

### Phase 2 (Authentication)
10. `src/ariel_bot/auth/password_manager.py` - Password logic
11. `src/ariel_bot/auth/allowlist.py` - Firestore user management
12. `src/ariel_bot/bot/handlers/start.py` - /start, /help
13. `src/ariel_bot/bot/handlers/auth.py` - Auth conversation
14. `src/ariel_bot/bot/middleware/auth_middleware.py` - Auth check

### Phase 3 (RAG Ingestion)
15. `scripts/create_vector_store.py` - Initialize File Search
16. `scripts/upload_documents.py` - Upload course materials
17. `src/ariel_bot/rag/document_processor.py` - Document utilities

### Phase 4 (RAG Q&A)
18. `src/ariel_bot/rag/file_search.py` - File Search integration
19. `src/ariel_bot/rag/citation_formatter.py` - Citation formatting
20. `src/ariel_bot/bot/handlers/question.py` - Q&A handler

### Phase 5 (Vision)
21. `src/ariel_bot/vision/image_processor.py` - Image download/validation
22. `src/ariel_bot/vision/ocr_service.py` - Gemini Vision integration
23. `src/ariel_bot/bot/handlers/vision.py` - Image handler

### Phase 6 (Polish)
24. `src/ariel_bot/utils/exceptions.py` - Custom exceptions
25. `src/ariel_bot/utils/rate_limiter.py` - Rate limiting
26. `src/ariel_bot/bot/application.py` - Bot setup

### Phase 7 (Deployment)
27. `Dockerfile` - Container definition
28. `.dockerignore` - Exclude from image
29. `docs/deployment.md` - Deployment guide

### Phase 8 (Testing)
30. `tests/unit/test_auth.py` - Auth unit tests
31. `tests/unit/test_rag.py` - RAG unit tests
32. `tests/unit/test_vision.py` - Vision unit tests
33. `tests/integration/test_bot_handlers.py` - Integration tests
34. `.github/workflows/ci.yml` - CI/CD pipeline

---

## First Steps

1. **Create project structure**: Set up directories following src layout
2. **Set up virtual environment**: `python -m venv venv` and activate
3. **Create `.gitignore`**: Prevent committing secrets
4. **Get API keys**:
   - Telegram: @BotFather → /newbot
   - Gemini: https://aistudio.google.com/apikey
   - GCP: Create project, enable APIs
5. **Create `.env`**: Copy from `.env.example`, fill in credentials
6. **Install dependencies**: `pip install -r requirements.txt`
7. **Test connections**: Run verification scripts
8. **Start Phase 1**: Build foundation before adding features

---

## Success Criteria

**MVP is complete when**:
- ✅ Users can authenticate with password
- ✅ Users can ask questions and get answers with citations
- ✅ Users can upload images and get solutions
- ✅ Rate limiting prevents abuse
- ✅ Bot is deployed to Cloud Run and accessible 24/7
- ✅ Error handling provides graceful degradation
- ✅ Logging enables debugging and monitoring
- ✅ Tests cover critical functionality (80%+ coverage)
- ✅ Documentation enables onboarding new developers

---

## Resources

**Official Documentation**:
- [python-telegram-bot docs](https://python-telegram-bot.readthedocs.io/)
- [Google Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search)
- [GCP Cloud Run docs](https://cloud.google.com/run/docs)
- [Firestore docs](https://cloud.google.com/firestore/docs)

**Learning Materials**:
- [Async Python tutorial](https://realpython.com/async-io-python/)
- [RAG systems explained](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Docker basics](https://docs.docker.com/get-started/)

---

## Notes

- This is a greenfield project - start simple and iterate
- Test incrementally after each phase
- Monitor costs with GCP billing alerts
- Use structured logging for debugging
- Document decisions and architecture changes
- Commit frequently with descriptive messages
- Follow Python best practices (type hints, docstrings, PEP 8)
