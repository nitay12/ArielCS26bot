"""Authentication conversation handler for password entry."""

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from auth.password_manager import verify_password
from auth.allowlist import add_user_to_allowlist

logger = logging.getLogger(__name__)

# Conversation states
AWAITING_PASSWORD = 1


async def verify_password_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle password verification during authentication conversation.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        int: ConversationHandler.END if successful, AWAITING_PASSWORD to retry

    Flow:
        1. Extract password from user message
        2. Verify password
        3. If correct: Add user to allowlist and end conversation
        4. If incorrect: Show error and allow retry
    """
    user = update.effective_user
    provided_password = update.message.text.strip()

    logger.info(f"Password verification attempt from user {user.id} ({user.username or 'no_username'})")

    try:
        # Verify password
        if verify_password(provided_password):
            # Password correct - add to allowlist
            logger.info(f"Successful authentication for user {user.id}")

            try:
                await add_user_to_allowlist(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )

                # Send success message
                success_message = (
                    f"✅ Authentication successful!\n\n"
                    f"Welcome to the Ariel CS 2026 Bot, {user.first_name}!\n\n"
                    f"I can help you with:\n"
                    f"📚 Answering questions about course materials\n"
                    f"🔍 Solving math problems from images\n\n"
                    f"Use /help to see all available commands."
                )
                await update.message.reply_text(success_message)

                return ConversationHandler.END

            except Exception as e:
                logger.error(f"Failed to add user {user.id} to allowlist: {e}")
                await update.message.reply_text(
                    "⚠️ An error occurred during authentication. "
                    "Please try again later or contact support."
                )
                return ConversationHandler.END

        else:
            # Password incorrect - allow retry
            logger.warning(f"Failed authentication attempt for user {user.id}")

            await update.message.reply_text(
                "❌ Incorrect password. Please try again or use /cancel to exit."
            )
            return AWAITING_PASSWORD

    except ValueError as e:
        # BOT_PASSWORD not configured
        logger.error(f"Configuration error during password verification: {e}")
        await update.message.reply_text(
            "⚠️ Bot configuration error. Please contact the administrator."
        )
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Unexpected error during password verification: {e}")
        await update.message.reply_text(
            "⚠️ An unexpected error occurred. Please try again later."
        )
        return ConversationHandler.END


async def cancel_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle /cancel command during authentication conversation.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        int: ConversationHandler.END to exit conversation
    """
    user = update.effective_user
    logger.info(f"User {user.id} cancelled authentication")

    await update.message.reply_text(
        "Authentication cancelled. Send /start when you're ready to authenticate."
    )

    return ConversationHandler.END
