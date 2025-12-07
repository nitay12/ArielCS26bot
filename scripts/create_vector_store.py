"""
Script to create Google File Search vector store for ArielCS26bot.

This script should be run once to initialize the File Search store.
The store ID will be saved to the .env file for use by other scripts.

Usage:
    python scripts/create_vector_store.py
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from google import genai
from google.genai import types
from config import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def update_env_file(env_path: Path, key: str, value: str) -> None:
    """
    Update .env file with new key-value pair.

    Preserves:
    - Comments (lines starting with #)
    - Blank lines
    - Other variables
    - Inline comments (after values)

    Args:
        env_path: Path to .env file
        key: Environment variable name
        value: Value to set

    Uses atomic write (temp file + rename) for safety.
    """
    # Read existing content
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = []

    # Find and update key
    updated = False
    new_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith(f"{key}="):
            # Update this line
            if '#' in stripped:
                # Preserve inline comment
                comment = '#' + stripped.split('#', 1)[1]
                new_lines.append(f"{key}={value} {comment}\n")
            else:
                new_lines.append(f"{key}={value}\n")
            updated = True
        else:
            new_lines.append(line)

    # Add key if not found
    if not updated:
        new_lines.append(f"{key}={value}\n")

    # Write atomically (temp file + rename)
    temp_path = env_path.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    temp_path.replace(env_path)
    logger.info(f"Updated .env: {key}={value}")


def create_file_search_store(client: genai.Client, display_name: str) -> types.FileSearchStore:
    """
    Create a new File Search store.

    Args:
        client: Gemini API client
        display_name: Human-readable name for the store

    Returns:
        FileSearchStore object

    Raises:
        google_exceptions.GoogleAPIError: API error occurred
    """
    logger.info(f"Creating File Search store: '{display_name}'...")

    store = client.file_search_stores.create(
        config=types.CreateFileSearchStoreConfig(
            display_name=display_name
        )
    )

    logger.info(f"Store created successfully!")
    logger.info(f"Store ID: {store.name}")

    return store


def main():
    """Main entry point for the script."""
    print("=" * 60)
    print("ArielCS26bot - File Search Store Creation")
    print("=" * 60)
    print()

    # Validate configuration
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in environment variables!")
        logger.error("Please add it to your .env file")
        logger.error("Get your key: https://aistudio.google.com/apikey")
        sys.exit(1)

    # Check if store already exists
    if settings.FILE_SEARCH_STORE_NAME:
        logger.warning(f"FILE_SEARCH_STORE_NAME already set: {settings.FILE_SEARCH_STORE_NAME}")
        response = input("Do you want to create a new store anyway? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            logger.info("Exiting without creating new store.")
            sys.exit(0)

    # Initialize Gemini client
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini API client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        sys.exit(1)

    # Create File Search store
    try:
        store = create_file_search_store(
            client=client,
            display_name='Ariel CS 2026 Knowledge Base'
        )
    except Exception as e:
        error_msg = str(e).lower()
        if 'unauthenticated' in error_msg or 'invalid' in error_msg or 'api key' in error_msg:
            logger.error("Authentication failed - Invalid GEMINI_API_KEY")
            logger.error("Please check your API key in .env")
        elif 'permission' in error_msg:
            logger.error("Permission denied - API key lacks required permissions")
        else:
            logger.error(f"Failed to create store: {e}")
        sys.exit(1)

    # Update .env file
    try:
        env_path = Path('.env')
        update_env_file(env_path, 'FILE_SEARCH_STORE_NAME', store.name)
    except Exception as e:
        logger.error(f"Failed to update .env file: {e}")
        logger.error(f"Please manually add: FILE_SEARCH_STORE_NAME={store.name}")
        sys.exit(1)

    # Success message
    print()
    print("=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print(f"✓ File Search store created: '{store.display_name}'")
    print(f"✓ Store ID: {store.name}")
    print(f"✓ Store ID saved to .env")
    print()
    print("Next steps:")
    print("  1. Run: pip install -r requirements.txt (to install tqdm)")
    print("  2. Run: python scripts/upload_documents.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
