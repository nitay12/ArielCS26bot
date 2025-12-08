"""
Script to verify File Search store setup with test queries.

This script tests the File Search store by running sample questions
and verifying that grounding metadata (citations) is returned.

Prerequisites:
    - Run scripts/create_vector_store.py
    - Run scripts/upload_documents.py
    - FILE_SEARCH_STORE_NAME must be set in .env

Usage:
    python scripts/verify_store.py
"""

import sys
import asyncio
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


def query_file_search(client: genai.Client, store_name: str, question: str) -> dict:
    """
    Query the File Search store with a question.

    Args:
        client: Gemini API client
        store_name: File Search store name
        question: Question to ask

    Returns:
        Dictionary with answer and grounding metadata
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=question,
        config=types.GenerateContentConfig(
            tools=[types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store_name]
                )
            )],
            temperature=0.3
        )
    )

    result = {
        'question': question,
        'answer': response.text,
        'has_grounding': False,
        'sources': []
    }

    # Extract grounding metadata from candidates
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
            result['has_grounding'] = True
            grounding_metadata = candidate.grounding_metadata

            if hasattr(grounding_metadata, 'grounding_chunks'):
                chunks = grounding_metadata.grounding_chunks
                for chunk in chunks:
                    if hasattr(chunk, 'retrieved_context'):
                        ctx = chunk.retrieved_context
                        source = {}
                        if hasattr(ctx, 'title'):
                            source['title'] = ctx.title
                        if hasattr(ctx, 'document_name'):
                            source['document'] = ctx.document_name
                        if source:
                            result['sources'].append(source)

    return result


async def main():
    """Main entry point for verification script."""
    print("=" * 60)
    print("ArielCS26bot - File Search Store Verification")
    print("=" * 60)
    print()

    # Validate configuration
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in .env")
        return

    if not settings.FILE_SEARCH_STORE_NAME:
        logger.error("FILE_SEARCH_STORE_NAME not found in .env")
        logger.error("Please run: python scripts/create_vector_store.py")
        return

    logger.info(f"Testing store: {settings.FILE_SEARCH_STORE_NAME}")
    print()

    # Initialize client
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini API client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
        return

    # Test questions
    test_questions = [
        "What topics are covered in calculus 1?",
        "Explain the concept of limits",
        "מה זה תורת הקבוצות?"  # Hebrew: What is set theory?
    ]

    print("Running test queries...")
    print()

    for i, question in enumerate(test_questions, 1):
        print(f"Query {i}/{len(test_questions)}")
        print("-" * 60)
        print(f"Q: {question}")
        print()

        try:
            # Run query in thread to avoid blocking
            result = await asyncio.to_thread(
                query_file_search,
                client,
                settings.FILE_SEARCH_STORE_NAME,
                question
            )

            # Display answer (truncated)
            answer = result['answer']
            if len(answer) > 300:
                answer = answer[:300] + "..."
            print(f"A: {answer}")
            print()

            # Display grounding info
            if result['has_grounding']:
                print(f"✓ Grounding: YES")
                if result['sources']:
                    print(f"Sources ({len(result['sources'])}):")
                    for source in result['sources'][:3]:
                        title = source.get('title', 'Unknown')
                        print(f"  - {title}")
            else:
                print("✗ Grounding: NO (no sources found)")

        except Exception as e:
            logger.error(f"Query failed: {e}")
            print(f"✗ Error: {e}")

        print()

    print("=" * 60)
    print("Verification complete!")
    print()
    print("If queries returned answers with grounding, your")
    print("File Search store is working correctly!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
