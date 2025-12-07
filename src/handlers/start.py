"""Start and help command handlers with authentication integration."""

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from auth.allowlist import is_user_authorized, update_last_active
from handlers.auth import AWAITING_PASSWORD

logger = logging.getLogger(__name__)


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle /start command - entry point for authentication conversation.

    This is the main entry point for users. It checks if the user is already
    authorized and branches accordingly:
    - Authorized users: See welcome back message
    - Unauthorized users: Prompted to enter password

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        int: ConversationHandler.END if authorized, AWAITING_PASSWORD if not
    """
    user = update.effective_user

    logger.info(f"/start command from user {user.id} ({user.username or 'no_username'})")

    try:
        # Check if user is already authorized
        if await is_user_authorized(user.id):
            # User is authorized - welcome back
            logger.info(f"Authorized user {user.id} accessed /start")

            # Update last active timestamp
            await update_last_active(user.id)

            # Send welcome back message
            welcome_message = (
                f"Welcome back, {user.first_name}! 👋\n\n"
                f"I'm ready to help you with:\n"
                f"📚 Course material questions\n"
                f"🔍 Math problem solving\n\n"
                f"Use /help for detailed information."
            )
            await update.message.reply_text(welcome_message)

            return ConversationHandler.END

        else:
            # User is not authorized - prompt for password
            logger.info(f"Unauthorized user {user.id} prompted for password")

            password_prompt = (
                f"Hello {user.first_name}! 👋\n\n"
                f"Welcome to the Ariel CS 2026 Bot.\n\n"
                f"This bot requires authentication to use.\n"
                f"Please enter the password:\n\n"
                f"(Use /cancel to exit)"
            )
            await update.message.reply_text(password_prompt)

            return AWAITING_PASSWORD

    except Exception as e:
        logger.error(f"Error in start_command for user {user.id}: {e}")
        await update.message.reply_text(
            "⚠️ An error occurred. Please try again later."
        )
        return ConversationHandler.END


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle /help command - shows bot features and commands.

    This command is protected by auth_filter, so only authorized users can access it.

    Args:
        update: Telegram update object
        context: Bot context
    """
    user = update.effective_user
    logger.info(f"/help command from user {user.id}")

    help_text = """
🤖 *Ariel CS 2026 Bot - Help*

*Commands:*
/start - Start the bot or re-authenticate
/help - Show this help message
/cancel - Cancel current operation

*Features:*

📚 *Ask Questions*
Just send your question as a text message and I'll search through course materials to provide answers with citations.

Example: "Explain the Sandwich Theorem"

🔍 *Upload Images*
Send a photo of a math problem (handwritten or printed) and I'll:
• Extract the problem using OCR
• Convert it to LaTeX format
• Provide a step-by-step solution

*Note:* More features are being developed!

For technical support or issues, please contact your course administrator.
    """

    await update.message.reply_text(help_text, parse_mode='Markdown')
