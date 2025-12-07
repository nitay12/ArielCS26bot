"""
Metadata extraction module for course materials.

Generates display names and metadata from file paths for better
organization in the File Search vector store.
"""

from pathlib import Path
from typing import Dict

# Mapping of course directory names to display names
COURSE_DISPLAY_NAMES = {
    'calculus_1': 'Calculus 1',
    'intro_to_cs': 'Introduction to CS',
    'linear_1': 'Linear Algebra 1',
    'set_theory_logic': 'Set Theory and Logic'
}


def extract_metadata(file_path: Path, course_name: str) -> Dict[str, str]:
    """
    Extract metadata for File Search from file path.

    Args:
        file_path: Path to the course material file
        course_name: Name of the course (directory name)

    Returns:
        Dictionary with metadata fields:
        {
            'display_name': 'Calculus 1 - infi_1_week_1_summary',
            'course': 'calculus_1',
            'filename': 'infi_1_week_1_summary.md',
            'file_type': 'md'
        }
    """
    # Get filename without extension
    filename = file_path.name
    file_stem = file_path.stem
    file_type = file_path.suffix.lstrip('.')

    # Generate display name
    display_name = get_display_name(course_name, file_stem)

    return {
        'display_name': display_name,
        'course': course_name,
        'filename': filename,
        'file_type': file_type
    }


def get_display_name(course_name: str, file_stem: str) -> str:
    """
    Generate human-readable display name for a file.

    Args:
        course_name: Name of the course (directory name)
        file_stem: Filename without extension

    Returns:
        Display name in format "Course Display Name - filename"
        Example: "Calculus 1 - infi_1_week_1_summary"
    """
    # Get beautified course name
    course_display = COURSE_DISPLAY_NAMES.get(
        course_name,
        course_name.replace('_', ' ').title()
    )

    # Combine course and filename
    return f"{course_display} - {file_stem}"


def get_course_display_name(course_name: str) -> str:
    """
    Get human-readable display name for a course.

    Args:
        course_name: Course directory name (e.g., 'calculus_1')

    Returns:
        Display name (e.g., 'Calculus 1')
    """
    return COURSE_DISPLAY_NAMES.get(
        course_name,
        course_name.replace('_', ' ').title()
    )
