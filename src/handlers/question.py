"""Question handler for RAG-based Q&A using Google File Search."""

import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from google import genai
from google.genai import types
from config import settings

logger = logging.getLogger(__name__)

# Constants
MAX_MESSAGE_LENGTH = 3800  # Leave buffer for sources + Telegram's 4096 limit
MAX_SOURCES = 5
GEMINI_MODEL = 'gemini-2.5-flash'
TEMPERATURE = 0.3


def _format_sources(grounding_metadata) -> str:
    """
    Extract and format sources from grounding metadata.

    Args:
        grounding_metadata: Response grounding metadata from Gemini

    Returns:
        Formatted string with numbered sources (max 5, deduplicated).
        Returns empty string if no sources found.
    """
    if not grounding_metadata:
        return ""

    if not hasattr(grounding_metadata, 'grounding_chunks'):
        return ""

    # Extract titles from chunks
    sources = []
    seen_titles = set()  # Deduplicate

    for chunk in grounding_metadata.grounding_chunks:
        if hasattr(chunk, 'retrieved_context'):
            ctx = chunk.retrieved_context

            # Prefer title over document_name
            title = None
            if hasattr(ctx, 'title') and ctx.title:
                title = ctx.title
            elif hasattr(ctx, 'document_name') and ctx.document_name:
                title = ctx.document_name

            if title and title not in seen_titles:
                sources.append(title)
                seen_titles.add(title)

                if len(sources) >= MAX_SOURCES:
                    break

    if not sources:
        return ""

    # Format as numbered list
    formatted = "\n\n📚 Sources:\n"
    for i, title in enumerate(sources, 1):
        formatted += f"{i}. {title}\n"

    return formatted


async def _query_file_search(
    client: genai.Client,
    store_name: str,
    question: str
) -> dict:
    """
    Query Gemini File Search store.

    Uses asyncio.to_thread() because Gemini SDK is synchronous.

    Args:
        client: Gemini API client
        store_name: File Search store name
        question: User's question

    Returns:
        Dictionary with structure:
        {
            'answer': str or None,
            'has_grounding': bool,
            'grounding_metadata': object or None,
            'error': str or None
        }
    """
    try:
        response = await asyncio.to_thread(
            lambda: client.models.generate_content(
                model=GEMINI_MODEL,
                contents=question,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store_name]
                        )
                    )],
                    temperature=TEMPERATURE
                )
            )
        )

        result = {
            'answer': response.text,
            'has_grounding': False,
            'grounding_metadata': None,
            'error': None
        }

        # Extract grounding metadata from candidates
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                result['has_grounding'] = True
                result['grounding_metadata'] = candidate.grounding_metadata

        return result

    except Exception as e:
        logger.error(f"File Search query failed: {e}")
        return {
            'answer': None,
            'has_grounding': False,
            'grounding_metadata': None,
            'error': str(e)
        }


async def question_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle text questions from authenticated users.

    Flow:
        1. Extract question from message
        2. Send "typing" indicator
        3. Initialize Gemini client
        4. Query File Search store
        5. Format response with sources
        6. Handle truncation if needed
        7. Send response to user

    Args:
        update: Telegram update object
        context: Bot context
    """
    user = update.effective_user
    question = update.message.text.strip()

    logger.info(f"Question from user {user.id}: {question[:50]}...")

    try:
        # Send typing indicator (shows bot is processing)
        await update.message.chat.send_action("typing")

        # Validate configuration
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not configured")
            await update.message.reply_text(
                "⚠️ Bot configuration error. Please contact the administrator."
            )
            return

        if not settings.FILE_SEARCH_STORE_NAME:
            logger.error("FILE_SEARCH_STORE_NAME not configured")
            await update.message.reply_text(
                "⚠️ Bot configuration error. Please contact the administrator."
            )
            return

        # Initialize Gemini client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # Query File Search
        result = await _query_file_search(
            client,
            settings.FILE_SEARCH_STORE_NAME,
            question
        )

        # Handle errors from query
        if result['error']:
            logger.error(f"Query error for user {user.id}: {result['error']}")
            await update.message.reply_text(
                "⚠️ I'm having trouble processing your question right now. "
                "Please try again in a moment."
            )
            return

        answer = result['answer']

        # Handle no results (no grounding metadata)
        if not result['has_grounding']:
            logger.info(f"No grounding for user {user.id} question")
            await update.message.reply_text(
                "❌ I couldn't find relevant information in the course materials.\n\n"
                "Try:\n"
                "• Rephrasing your question\n"
                "• Being more specific\n"
                "• Asking about topics covered in the course"
            )
            return

        # Format sources
        sources = _format_sources(result['grounding_metadata'])

        # Combine answer and sources
        full_response = answer + sources

        # Handle message length (Telegram limit: 4096 chars)
        if len(full_response) > MAX_MESSAGE_LENGTH:
            logger.warning(f"Response truncated for user {user.id} (length: {len(full_response)})")

            # Calculate available space for answer
            truncation_note = "\n\n... [Answer truncated - try asking more specific questions]"
            available_length = MAX_MESSAGE_LENGTH - len(sources) - len(truncation_note)

            # Truncate answer, keep sources intact
            truncated_answer = answer[:available_length]
            full_response = truncated_answer + truncation_note + sources

        # Send response
        await update.message.reply_text(full_response)
        logger.info(f"Successfully answered question for user {user.id}")

    except TimeoutError as e:
        logger.warning(f"Timeout for user {user.id}: {e}")
        await update.message.reply_text(
            "⏱️ The search is taking longer than expected. "
            "Please try again in a moment."
        )

    except Exception as e:
        logger.error(f"Unexpected error handling question for user {user.id}: {e}", exc_info=True)
        await update.message.reply_text(
            "⚠️ An unexpected error occurred. Please try again later."
        )
