"""Password verification for bot authentication."""

import logging
from config import settings

logger = logging.getLogger(__name__)


def verify_password(provided_password: str) -> bool:
    """
    Verify provided password against BOT_PASSWORD from configuration.

    Args:
        provided_password: Password string provided by the user

    Returns:
        bool: True if password matches, False otherwise

    Raises:
        ValueError: If BOT_PASSWORD is not configured in environment

    Security:
        - Never logs passwords
        - Case-sensitive comparison
        - Strips leading/trailing whitespace from input
    """
    if not settings.BOT_PASSWORD:
        logger.error("BOT_PASSWORD not configured in environment")
        raise ValueError("BOT_PASSWORD not configured. Please set it in .env file")

    # Strip whitespace and compare
    cleaned_password = provided_password.strip()

    # Log verification attempt (without exposing password)
    logger.debug("Password verification attempt")

    return cleaned_password == settings.BOT_PASSWORD
