"""
Script to upload all course materials to Google File Search store.

This script scans the data/course_materials directory and uploads all
supported files to the File Search store for use with the RAG system.

Prerequisites:
    - Run scripts/create_vector_store.py first
    - FILE_SEARCH_STORE_NAME must be set in .env

Usage:
    python scripts/upload_documents.py
"""

import sys
import asyncio
import logging
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from google import genai
from tqdm import tqdm

from config import settings
from rag.file_scanner import scan_course_materials
from rag.metadata_extractor import extract_metadata, get_course_display_name
from rag.document_processor import upload_document

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the upload script."""
    print("=" * 60)
    print("ArielCS26bot - Course Materials Upload")
    print("=" * 60)
    print()

    # 1. Validate configuration
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in .env")
        logger.error("Please add your Gemini API key to .env")
        logger.error("Get your key: https://aistudio.google.com/apikey")
        return

    if not settings.FILE_SEARCH_STORE_NAME:
        logger.error("FILE_SEARCH_STORE_NAME not found in .env")
        logger.error("Please run: python scripts/create_vector_store.py")
        return

    logger.info(f"Using File Search store: {settings.FILE_SEARCH_STORE_NAME}")

    # 2. Initialize Gemini client
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini API client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        return

    # 3. Scan course materials
    materials_dir = Path("data/course_materials")
    if not materials_dir.exists():
        logger.error(f"Directory not found: {materials_dir}")
        logger.error("Please create the directory and add course materials")
        return

    logger.info(f"Scanning {materials_dir}...")
    files = scan_course_materials(materials_dir)

    if not files:
        logger.warning("No files found to upload")
        logger.warning(f"Please add course materials to {materials_dir}")
        return

    logger.info(f"Found {len(files)} files to upload")
    print()

    # Check current store status
    try:
        store_info = client.file_search_stores.get(name=settings.FILE_SEARCH_STORE_NAME)
        current_docs = store_info.active_documents_count or 0
        if current_docs > 0:
            print(f"WARNING: Store currently has {current_docs} documents")
            print("         Running this script will add duplicates!")
            print()
            print("   To avoid duplicates:")
            print("   1. Clean the store first:")
            print("      python scripts/cleanup_duplicates.py --delete-all")
            print("   2. Or skip files that are already uploaded (coming soon)")
            print()
    except Exception as e:
        logger.warning(f"Could not check store status: {e}")

    # Display breakdown by course
    courses = {}
    for _, course in files:
        courses[course] = courses.get(course, 0) + 1

    print("Files by course:")
    for course, count in sorted(courses.items()):
        course_display = get_course_display_name(course)
        print(f"  - {course_display}: {count} files")
    print()

    # Confirm upload (check for --yes flag to skip confirmation)
    if '--yes' not in sys.argv and '-y' not in sys.argv:
        try:
            response = input(f"Upload {len(files)} files to File Search? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                logger.info("Upload cancelled by user")
                return
        except (EOFError, KeyboardInterrupt):
            print("\nUse --yes or -y flag to skip confirmation")
            return

    print()
    print("Starting upload...")
    print()

    # 4. Upload with progress tracking
    results = []

    with tqdm(total=len(files), desc="Uploading", unit="file") as pbar:
        for file_path, course in files:
            # Extract metadata
            metadata = extract_metadata(file_path, course)

            # Update progress bar description
            pbar.set_postfix({'file': file_path.name[:30]})

            # Upload document
            result = await upload_document(
                client=client,
                store_name=settings.FILE_SEARCH_STORE_NAME,
                file_path=file_path,
                metadata=metadata
            )

            results.append(result)

            # Move file to 'uploaded' directory if successful
            if result['status'] == 'success':
                try:
                    # Get the course directory
                    course_dir = materials_dir / course
                    uploaded_dir = course_dir / 'uploaded'

                    # Create 'uploaded' directory if it doesn't exist
                    uploaded_dir.mkdir(parents=True, exist_ok=True)

                    # Move file while preserving relative structure within to_upload
                    to_upload_dir = course_dir / 'to_upload'
                    relative_path = file_path.relative_to(to_upload_dir)
                    destination = uploaded_dir / relative_path

                    # Create parent directories in uploaded if needed
                    destination.parent.mkdir(parents=True, exist_ok=True)

                    # Move the file
                    shutil.move(str(file_path), str(destination))
                    logger.info(f"Moved {file_path.name} to uploaded directory")

                except Exception as e:
                    logger.warning(f"Failed to move {file_path.name}: {e}")

            pbar.update(1)

            # Brief pause to avoid rate limiting
            await asyncio.sleep(0.5)

    # 5. Display summary
    print()
    print("=" * 60)
    print("UPLOAD SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']

    print(f"Total files: {len(results)}")
    print(f"[OK] Successful: {len(successful)}")
    print(f"[FAIL] Failed: {len(failed)}")
    print()

    if failed:
        print("Failed uploads:")
        for result in failed:
            print(f"  - {result['file_name']}: {result['error']}")
        print()

    if successful:
        print("All files uploaded successfully!")
        print()
        print("Next steps:")
        print("  1. Verify upload in Google AI Studio:")
        print("     https://aistudio.google.com/")
        print("  2. Test the store:")
        print("     python scripts/verify_store.py")
    else:
        print("No files were uploaded successfully.")
        print("Please check the errors above and try again.")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
