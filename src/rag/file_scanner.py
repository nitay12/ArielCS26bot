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
    Scan directory tree for course material files.

    Args:
        root_dir: Path to data/course_materials/ directory

    Returns:
        List of (file_path, course_name) tuples
        Example: [
            (Path('.../calculus_1/week1.md'), 'calculus_1'),
            (Path('.../set_theory_logic/lecture1.pdf'), 'set_theory_logic')
        ]

    The course name is extracted from the parent directory name.
    Hidden files and directories (starting with '.') are skipped.
    """
    if not root_dir.exists():
        logger.warning(f"Directory does not exist: {root_dir}")
        return []

    if not root_dir.is_dir():
        logger.error(f"Path is not a directory: {root_dir}")
        return []

    files = []

    # Recursively scan for files
    for file_path in root_dir.rglob('*'):
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

        # Extract course name from parent directory
        # Skip if file is directly in root (no course directory)
        if file_path.parent == root_dir:
            logger.warning(f"Skipping file in root directory: {file_path.name}")
            continue

        course_name = file_path.parent.name

        files.append((file_path, course_name))

    logger.info(f"Found {len(files)} files in {root_dir}")

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
