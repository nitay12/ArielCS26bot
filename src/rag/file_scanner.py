"""
File scanner module for discovering course materials.

Recursively scans directories for supported document types and extracts
course information from the directory structure.
"""

import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Supported file extensions for course materials
SUPPORTED_EXTENSIONS = {'.pdf', '.md', '.docx', '.txt'}


def scan_course_materials(root_dir: Path) -> List[Tuple[Path, str]]:
    """
    Scan directory tree for course material files in 'to_upload' subdirectories.

    Args:
        root_dir: Path to data/course_materials/ directory

    Returns:
        List of (file_path, course_name) tuples
        Example: [
            (Path('.../calculus_1/to_upload/week1.md'), 'calculus_1'),
            (Path('.../set_theory_logic/to_upload/lecture1.pdf'), 'set_theory_logic')
        ]

    The course name is extracted from the parent directory of the 'to_upload' folder.
    Hidden files and directories (starting with '.') are skipped.
    Only files in 'to_upload' subdirectories are included.
    """
    if not root_dir.exists():
        logger.warning(f"Directory does not exist: {root_dir}")
        return []

    if not root_dir.is_dir():
        logger.error(f"Path is not a directory: {root_dir}")
        return []

    files = []

    # Scan for 'to_upload' directories in each course folder
    for course_dir in root_dir.iterdir():
        # Skip files in root
        if not course_dir.is_dir():
            continue

        # Skip hidden directories
        if course_dir.name.startswith('.'):
            continue

        course_name = course_dir.name
        to_upload_dir = course_dir / 'to_upload'

        # Skip if no to_upload directory exists
        if not to_upload_dir.exists() or not to_upload_dir.is_dir():
            logger.debug(f"No to_upload directory for course: {course_name}")
            continue

        # Scan files in to_upload directory
        for file_path in to_upload_dir.rglob('*'):
            # Skip if not a file
            if not file_path.is_file():
                continue

            # Skip hidden files
            if any(part.startswith('.') for part in file_path.parts):
                continue

            # Check if extension is supported
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                logger.debug(f"Skipping unsupported file type: {file_path}")
                continue

            files.append((file_path, course_name))

    logger.info(f"Found {len(files)} files in to_upload directories")

    return files


def get_files_by_course(root_dir: Path) -> dict[str, List[Path]]:
    """
    Scan and group files by course.

    Args:
        root_dir: Path to data/course_materials/ directory

    Returns:
        Dictionary mapping course names to lists of file paths
        Example: {
            'calculus_1': [Path('week1.md'), Path('week2.md')],
            'set_theory_logic': [Path('lecture1.pdf')]
        }
    """
    files = scan_course_materials(root_dir)

    courses = {}
    for file_path, course_name in files:
        if course_name not in courses:
            courses[course_name] = []
        courses[course_name].append(file_path)

    return courses
