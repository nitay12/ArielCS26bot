# Ariel CS 2026 Telegram Bot

An AI-powered Telegram bot for Computer Science students at Ariel University. The bot provides RAG-based Q&A using course materials, vision-based problem solving, and password-protected access.

## Features

- 📚 **RAG-based Q&A**: Ask questions and get answers from course materials with citations
- 👁️ **Vision Helper**: Upload images of math problems for step-by-step solutions
- 🛡️ **Secure Access**: Password-protected bot for verified students only

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
```

### 5. Run the Bot

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
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration management
│   ├── auth.py              # Authentication (coming soon)
│   ├── bot_handlers.py      # Message handlers (coming soon)
│   ├── rag_service.py       # RAG Q&A (coming soon)
│   └── vision_service.py    # Image processing (coming soon)
├── data/
│   ├── users.json           # User allowlist
│   └── course_materials/    # Course PDFs
├── scripts/
│   ├── setup_vector_store.py  # Vector store setup (coming soon)
│   └── upload_docs.py          # Document upload (coming soon)
├── .env                     # Environment variables (not in git)
├── .env.example             # Template for .env
├── requirements.txt         # Python dependencies
└── README.md
```

## Development Status

This is a local development version. Current implementation:

- ✅ Phase 1: Basic bot setup with `/start` and `/help` commands
- ⏳ Phase 2: Authentication system
- ⏳ Phase 3: RAG document upload
- ⏳ Phase 4: Q&A feature
- ⏳ Phase 5: Vision feature

## Usage

Once fully implemented:

### Ask Questions
Simply send a text message with your question:
```
"Explain the Sandwich Theorem"
```

### Upload Images
Send a photo of a math problem, and the bot will:
1. Extract the problem using OCR
2. Convert to LaTeX format
3. Provide a step-by-step solution

## Troubleshooting

### Bot doesn't start
- Make sure your `.env` file exists and has valid credentials
- Check that your virtual environment is activated
- Verify Python version: `python --version` (should be 3.10+)

### "TELEGRAM_TOKEN not found" error
- Make sure you copied `.env.example` to `.env`
- Verify the token is correctly pasted (no extra spaces)

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
