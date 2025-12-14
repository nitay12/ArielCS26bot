"""
Script to remove duplicate documents from File Search store.

This script lists all documents in the store and helps identify/remove duplicates
based on display names.

Prerequisites:
    - FILE_SEARCH_STORE_NAME must be set in .env

Usage:
    python scripts/cleanup_duplicates.py [--dry-run] [--delete-all]

Options:
    --dry-run     : Show what would be deleted without actually deleting
    --delete-all  : Delete the entire store and recreate it (fastest option)
"""

import sys
import asyncio
import logging
from pathlib import Path
from collections import defaultdict

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


async def list_all_documents(client: genai.Client, store_name: str) -> list:
    """List all documents in the File Search store."""
    documents = []

    try:
        # Note: This API might not be available in all regions
        # Alternative: Store might need to be managed via Google AI Studio
        page_token = None

        while True:
            config = types.ListDocumentsConfig(
                page_size=20,  # Max allowed by API
                page_token=page_token
            )

            response = await asyncio.to_thread(
                lambda: client.file_search_stores.documents.list(
                    parent=store_name,
                    config=config
                )
            )

            for doc in response:
                documents.append(doc)

            # Check if there are more pages
            if not hasattr(response, 'next_page_token') or not response.next_page_token:
                break
            page_token = response.next_page_token

    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        logger.error("Document listing may not be available for your API endpoint.")
        logger.error("You may need to use Google AI Studio to manage documents:")
        logger.error("https://aistudio.google.com/")
        return None

    return documents


async def delete_all_documents(client: genai.Client, store_name: str) -> int:
    """Delete all documents from the store."""
    deleted_count = 0

    try:
        # List all documents
        logger.info("Listing all documents in store...")
        documents = []
        page_token = None

        while True:
            try:
                config = types.ListDocumentsConfig(
                    page_size=20,  # Max allowed by API
                    page_token=page_token
                )

                response = await asyncio.to_thread(
                    lambda: client.file_search_stores.documents.list(
                        parent=store_name,
                        config=config
                    )
                )

                for doc in response:
                    documents.append(doc)

                # Check if there are more pages
                if not hasattr(response, 'next_page_token') or not response.next_page_token:
                    break
                page_token = response.next_page_token
            except Exception as e:
                logger.error(f"Error listing documents: {e}")
                break

        if not documents:
            logger.info("No documents found in store")
            return 0

        logger.info(f"Found {len(documents)} documents to delete")
        print(f"Deleting {len(documents)} documents...")
        print()

        # Delete each document with progress
        from tqdm import tqdm

        with tqdm(total=len(documents), desc="Deleting", unit="doc") as pbar:
            for doc in documents:
                try:
                    await asyncio.to_thread(
                        lambda d=doc: client.file_search_stores.documents.delete(
                            name=d.name,
                            config=types.DeleteDocumentConfig(force=True)
                        )
                    )
                    deleted_count += 1
                    pbar.update(1)
                except Exception as e:
                    logger.error(f"Failed to delete {doc.name}: {e}")
                    pbar.update(1)

        return deleted_count

    except Exception as e:
        logger.error(f"Failed to delete documents: {e}")
        return deleted_count


async def main():
    """Main entry point for cleanup script."""
    print("=" * 60)
    print("ArielCS26bot - File Search Store Cleanup")
    print("=" * 60)
    print()

    dry_run = '--dry-run' in sys.argv
    delete_all = '--delete-all' in sys.argv

    if dry_run:
        print("[DRY RUN MODE] - No changes will be made")
        print()

    # Validate configuration
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in .env")
        return

    if not settings.FILE_SEARCH_STORE_NAME:
        logger.error("FILE_SEARCH_STORE_NAME not found in .env")
        return

    # Initialize client
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini API client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
        return

    # Get current store info
    try:
        store = await asyncio.to_thread(
            lambda: client.file_search_stores.get(name=settings.FILE_SEARCH_STORE_NAME)
        )
        print(f"Current store: {store.name}")
        print(f"Display name: {store.display_name}")
        print(f"Active documents: {store.active_documents_count}")
        print()
    except Exception as e:
        logger.error(f"Failed to get store info: {e}")
        return

    if delete_all:
        print("WARNING: This will DELETE ALL documents from the store!")
        print("The store itself will remain, but all documents will be removed.")
        print("You will need to re-run upload_documents.py afterwards.")
        print()

        if '--yes' not in sys.argv:
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                logger.info("Operation cancelled")
                return

        print()

        if dry_run:
            print("[DRY RUN] Would delete all documents from store")
        else:
            deleted_count = await delete_all_documents(client, settings.FILE_SEARCH_STORE_NAME)
            print()
            if deleted_count > 0:
                print(f"[OK] Successfully deleted {deleted_count} documents!")
                print()
                print("Store is now empty. To re-upload files:")
                print("  python scripts/upload_documents.py")
            else:
                print("[INFO] No documents were deleted (store may already be empty)")

        return

    # Try to list documents (may not be available in all regions)
    print("Attempting to list documents...")
    documents = await list_all_documents(client, settings.FILE_SEARCH_STORE_NAME)

    if documents is None:
        print()
        print("WARNING: Document listing is not available for your API endpoint.")
        print()
        print("Options:")
        print("  1. Delete and recreate the store:")
        print("     python scripts/cleanup_duplicates.py --delete-all")
        print()
        print("  2. Manage documents via Google AI Studio:")
        print("     https://aistudio.google.com/")
        print()
        print("Recommendation: Use --delete-all for a clean slate")
        return

    if not documents:
        print("No documents found in store")
        return

    # Group by display name to find duplicates
    by_name = defaultdict(list)
    for doc in documents:
        display_name = doc.display_name if hasattr(doc, 'display_name') else doc.name
        by_name[display_name].append(doc)

    # Find duplicates
    duplicates = {name: docs for name, docs in by_name.items() if len(docs) > 1}

    if not duplicates:
        print(f"[OK] No duplicates found! All {len(documents)} documents are unique.")
        return

    print(f"Found {len(duplicates)} files with duplicates:")
    print()

    total_to_delete = 0
    for name, docs in sorted(duplicates.items()):
        print(f"  {name}: {len(docs)} copies")
        total_to_delete += len(docs) - 1  # Keep one, delete the rest

    print()
    print(f"Total documents to delete: {total_to_delete}")
    print(f"Documents to keep: {len(documents) - total_to_delete}")
    print()

    if dry_run:
        print("[DRY RUN] Would delete duplicates (keeping one copy of each)")
        return

    # Ask for confirmation
    response = input(f"Delete {total_to_delete} duplicate documents? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        logger.info("Operation cancelled")
        return

    # Delete duplicates (keep the first one, delete the rest)
    print()
    print("Deleting duplicates...")
    deleted_count = 0

    for name, docs in duplicates.items():
        # Keep the first document, delete the rest
        for doc in docs[1:]:
            try:
                await asyncio.to_thread(
                    lambda d=doc: client.file_search_stores.documents.delete(
                        name=d.name,
                        config=types.DeleteDocumentConfig(force=True)
                    )
                )
                deleted_count += 1
                logger.info(f"Deleted: {doc.name}")
            except Exception as e:
                logger.error(f"Failed to delete {doc.name}: {e}")

    print()
    print(f"[OK] Deleted {deleted_count} duplicate documents")
    print()
    print("Cleanup complete!")


if __name__ == "__main__":
    asyncio.run(main())
