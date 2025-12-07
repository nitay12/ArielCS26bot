import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from config import settings
from handlers.start import start_command, help_command
from handlers.auth import verify_password_handler, cancel_handler, AWAITING_PASSWORD
from middleware.auth_middleware import auth_filter


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot in polling mode with authentication system."""
    # Validate configuration
    if not settings.TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not found in environment variables!")
        logger.error("Please create a .env file based on .env.example")
        return

    if not settings.BOT_PASSWORD:
        logger.error("BOT_PASSWORD not found in environment variables!")
        logger.error("Please set BOT_PASSWORD in your .env file")
        return

    logger.info("Creating bot application...")
    application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    # Authentication ConversationHandler (must be registered first!)
    auth_conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            AWAITING_PASSWORD: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    verify_password_handler
                )
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
        name="authentication",
        persistent=False
    )

    # Register handlers (ORDER MATTERS!)
    application.add_handler(auth_conversation)  # Must be first
    application.add_handler(CommandHandler("help", help_command, filters=auth_filter))

    # Future handlers for Phase 3+ will go here:
    # application.add_handler(MessageHandler(
    #     auth_filter & filters.TEXT & ~filters.COMMAND,
    #     question_handler
    # ))
    # application.add_handler(MessageHandler(
    #     auth_filter & filters.PHOTO,
    #     image_handler
    # ))

    # Start polling
    logger.info("Bot is running in polling mode with authentication...")
    logger.info("Press Ctrl+C to stop the bot")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
