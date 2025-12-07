"""Authorization middleware/filter to block unauthorized users."""

import logging
from telegram.ext import filters

from auth.allowlist import is_user_authorized

logger = logging.getLogger(__name__)


class AuthFilter(filters.MessageFilter):
    """
    Custom filter that checks if a user is authorized to use the bot.

    This filter blocks unauthorized users from accessing protected bot features.
    It checks the user's ID against the allowlist.

    Usage:
        # Apply to handlers that require authentication
        application.add_handler(
            CommandHandler("help", help_command, filters=auth_filter)
        )

        # Combine with other filters
        application.add_handler(
            MessageHandler(
                auth_filter & filters.TEXT & ~filters.COMMAND,
                message_handler
            )
        )
    """

    name = 'AuthFilter'

    async def filter(self, message) -> bool:
        """
        Check if the message sender is authorized.

        Args:
            message: Telegram message object

        Returns:
            bool: True if user is authorized, False otherwise

        Note:
            Returns False for messages without a user (shouldn't happen in practice)
        """
        if not message.from_user:
            logger.warning("Received message without from_user")
            return False

        user_id = message.from_user.id

        # Check authorization
        authorized = await is_user_authorized(user_id)

        if not authorized:
            logger.debug(f"Blocked unauthorized access attempt from user {user_id}")

        return authorized


# Create singleton instance for use in handlers
auth_filter = AuthFilter()
