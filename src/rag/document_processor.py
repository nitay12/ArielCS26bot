"""
Document processor module for uploading files to Google File Search.

Provides async wrappers around the synchronous Google GenAI SDK for
uploading documents and managing File Search operations.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict

from google import genai
from google.genai import types

# Configure logging to handle Unicode properly
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding='utf-8',
    force=True
)
logger = logging.getLogger(__name__)


async def upload_file_to_gemini(
    client: genai.Client,
    file_path: Path,
    display_name: str
) -> types.File:
    """
    Upload file to Gemini Files API.

    Args:
        client: Gemini API client
        file_path: Path to file to upload
        display_name: Human-readable name for the file

    Returns:
        File object from Gemini API

    Note:
        Uses asyncio.to_thread() because the Gemini SDK is synchronous
    """
    logger.info(f"Uploading {file_path.name} to Gemini Files API...")

    file_obj = await asyncio.to_thread(
        client.files.upload,
        file=str(file_path),
        config=types.UploadFileConfig(
            display_name=display_name
        )
    )

    logger.debug(f"File uploaded: {file_obj.name}")
    return file_obj


async def add_file_to_store(
    client: genai.Client,
    store_name: str,
    file: types.File
) -> types.Operation:
    """
    Add uploaded file to File Search store.

    Args:
        client: Gemini API client
        store_name: Name of the File Search store
        file: File object from Files API

    Returns:
        Operation object for tracking completion
    """
    logger.debug(f"Adding {file.name} to store {store_name}...")

    # Correct parameter name is 'file_search_store_name', not 'name'
    # See: https://github.com/googleapis/python-genai/issues/1638
    operation = await asyncio.to_thread(
        lambda: client.file_search_stores.upload_to_file_search_store(
            file=file.name,
            file_search_store_name=store_name
        )
    )

    return operation


async def wait_for_operation(
    client: genai.Client,
    operation,
    timeout: int = 300,
    poll_interval: float = 2.0
) -> None:
    """
    Poll operation until complete or timeout.

    Args:
        client: Gemini API client
        operation: Operation object returned from upload_to_file_search_store
        timeout: Maximum time to wait in seconds
        poll_interval: Time between status checks in seconds

    Raises:
        TimeoutError: Operation didn't complete in time
        RuntimeError: Operation failed with error
    """
    start_time = asyncio.get_event_loop().time()

    while True:
        # Refresh operation status
        # operations.get() expects an Operation object and extracts its .name internally
        current_op = await asyncio.to_thread(
            lambda: client.operations.get(operation)
        )

        if current_op.done:
            if hasattr(current_op, 'error') and current_op.error:
                raise RuntimeError(f"Operation failed: {current_op.error}")
            logger.debug(f"Operation completed successfully")
            return

        # Check timeout
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"Operation timed out after {timeout}s")

        await asyncio.sleep(poll_interval)


async def upload_document(
    client: genai.Client,
    store_name: str,
    file_path: Path,
    metadata: Dict[str, str]
) -> Dict[str, str]:
    """
    Upload document to File Search (complete pipeline).

    Uses upload_to_file_search_store which handles both uploading and indexing in one operation.

    Args:
        client: Gemini API client
        store_name: Name of the File Search store
        file_path: Path to file to upload
        metadata: File metadata (must include 'display_name')

    Returns:
        Result dictionary:
        {
            'file_id': 'files/abc123' or None,
            'file_name': 'filename.pdf',
            'status': 'success' or 'failed',
            'error': None or error message
        }
    """
    try:
        # Log with ASCII-safe representation for Hebrew filenames
        safe_name = file_path.name.encode('ascii', 'replace').decode('ascii')
        logger.info(f"Uploading to File Search store: {safe_name}")

        # Use upload_to_file_search_store which handles upload + indexing in one call
        # See: https://github.com/googleapis/python-genai/issues/1638
        operation = await asyncio.to_thread(
            lambda: client.file_search_stores.upload_to_file_search_store(
                file=str(file_path),
                file_search_store_name=store_name,
                config={'display_name': metadata['display_name']}
            )
        )

        # Wait for processing
        await wait_for_operation(client, operation)

        logger.info(f"Successfully uploaded: {safe_name}")

        return {
            'file_id': str(operation) if operation else None,
            'file_name': file_path.name,
            'status': 'success',
            'error': None
        }

    except FileNotFoundError:
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        return {
            'file_id': None,
            'file_name': file_path.name,
            'status': 'failed',
            'error': error_msg
        }

    except TimeoutError as e:
        error_msg = f"Processing timed out: {str(e)}"
        logger.warning(f"{error_msg}. File may still be processing.")
        return {
            'file_id': None,
            'file_name': file_path.name,
            'status': 'failed',
            'error': error_msg
        }

    except Exception as e:
        error_msg = f"Upload failed: {str(e)}"
        logger.error(f"Failed to upload {file_path}: {e}")
        return {
            'file_id': None,
            'file_name': file_path.name,
            'status': 'failed',
            'error': error_msg
        }
