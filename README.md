# Ariel CS 2026 Telegram Bot

An AI-powered Telegram bot for Computer Science students at Ariel University. The bot provides RAG-based Q&A using course materials, vision-based problem solving, and password-protected access.

## Features

- 📚 **RAG-based Q&A**: Ask questions and get answers from course materials with source citations
- 🔍 **Google File Search**: Advanced vector search using Google's File Search API for accurate retrieval
- 🛡️ **Secure Access**: Password-protected authentication with user allowlist management
- 📄 **Document Management**: Automated scripts for uploading, verifying, and cleaning up course materials
- 👁️ **Vision Helper** (Coming Soon): Upload images of math problems for step-by-step solutions

## Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- A Telegram account
- Google Gemini API key

### 2. Installation

```bash
# Clone or navigate to the project directory
cd "C:\Users\user\Desktop\python projects\ArielCS26bot"

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Get API Credentials

#### Telegram Bot Token:
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Copy the token provided

#### Google Gemini API Key:
1. Visit https://aistudio.google.com/apikey
2. Create a new API key
3. Copy the key

### 4. Configure Environment Variables

```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your credentials:
# - TELEGRAM_TOKEN=your_telegram_bot_token
# - GEMINI_API_KEY=your_gemini_api_key
# - BOT_PASSWORD=your_custom_password
# - VECTOR_STORE_ID=your_google_file_search_store_id (created by running scripts/create_vector_store.py)
```

### 5. Set Up Vector Store (First Time Only)

```bash
# Create the Google File Search vector store
python scripts/create_vector_store.py

# Upload course materials to the vector store
python scripts/upload_documents.py

# Verify the upload
python scripts/verify_store.py
```

### 6. Run the Bot

```bash
# Make sure your virtual environment is activated
python src/main.py
```

The bot will start in polling mode. Open Telegram and search for your bot by name, then send `/start`!

## Project Structure

```
ArielCS26bot/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point with bot setup
│   ├── config.py            # Configuration management
│   ├── auth/
│   │   ├── password_manager.py  # Password verification
│   │   └── allowlist.py         # User allowlist management
│   ├── handlers/
│   │   ├── start.py         # /start and /help commands
│   │   ├── auth.py          # Authentication flow
│   │   └── question.py      # RAG-based Q&A handler
│   ├── middleware/
│   │   └── auth_middleware.py  # Authentication filter
│   └── rag/
│       ├── document_processor.py  # PDF processing
│       ├── metadata_extractor.py  # Document metadata extraction
│       └── file_scanner.py        # Course materials scanner
├── data/
│   ├── users.json           # User allowlist
│   └── course_materials/    # Course PDFs (upload here)
├── scripts/
│   ├── create_vector_store.py   # Initialize Google File Search store
│   ├── upload_documents.py      # Upload docs to vector store
│   ├── verify_store.py          # Verify vector store contents
│   └── cleanup_duplicates.py    # Remove duplicate documents
├── .env                     # Environment variables (not in git)
├── .env.example             # Template for .env
├── requirements.txt         # Python dependencies
└── README.md
```

## Development Status

Current implementation status:

- ✅ Phase 1: Basic bot setup with `/start` and `/help` commands
- ✅ Phase 2: Authentication system with password verification and user allowlist
- ✅ Phase 3: Google File Search vector store integration
- ✅ Phase 4: RAG-based Q&A feature with source citations
- ⏳ Phase 5: Vision feature (image processing for math problems)

## Usage

### First Time Setup
1. Start the bot by sending `/start`
2. Enter the bot password when prompted
3. Your Telegram user ID will be added to the allowlist

### Ask Questions
Simply send a text message with your question about course materials:
```
"Explain the Sandwich Theorem"
"What is the definition of a limit?"
"How do I solve differential equations?"
```

The bot will:
- Search through uploaded course materials using Google File Search
- Generate an answer based on relevant content
- Provide source citations showing which documents were used

### Commands
- `/start` - Start the bot and authenticate
- `/help` - Show available commands and usage instructions
- `/cancel` - Cancel the current authentication process

### Upload Images (Coming Soon)
Send a photo of a math problem, and the bot will:
1. Extract the problem using OCR
2. Convert to LaTeX format
3. Provide a step-by-step solution

## Document Management Scripts

The project includes several utility scripts for managing course materials:

### Create Vector Store
```bash
python scripts/create_vector_store.py
```
Creates a new Google File Search vector store and saves the ID to your `.env` file.

### Upload Documents
```bash
python scripts/upload_documents.py
```
Scans the `data/course_materials/` folder and uploads all PDFs to the vector store. Shows progress bar and handles errors gracefully.

### Verify Store
```bash
python scripts/verify_store.py
```
Lists all documents currently in the vector store to verify successful uploads.

### Cleanup Duplicates
```bash
python scripts/cleanup_duplicates.py
```
Removes duplicate documents from the vector store, keeping the most recent version of each file.

## Troubleshooting

### Bot doesn't start
- Make sure your `.env` file exists and has valid credentials
- Check that your virtual environment is activated
- Verify Python version: `python --version` (should be 3.10+)
- Ensure `VECTOR_STORE_ID` is set (run `create_vector_store.py` if needed)

### "TELEGRAM_TOKEN not found" error
- Make sure you copied `.env.example` to `.env`
- Verify the token is correctly pasted (no extra spaces)

### "VECTOR_STORE_ID not found" error
- Run `python scripts/create_vector_store.py` to create a vector store
- The script will automatically update your `.env` file

### Bot returns "No relevant information found"
- Make sure you've uploaded documents using `upload_documents.py`
- Verify documents are in the store using `verify_store.py`
- Check that PDFs are in `data/course_materials/` folder

### Dependencies not installing
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then try again
pip install -r requirements.txt
```

## Contributing

This is a student project. If you find bugs or have suggestions, feel free to open an issue.

## License

Educational project for Ariel University CS students.
