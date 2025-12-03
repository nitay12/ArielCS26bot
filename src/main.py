import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import settings


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command"""
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n\n"
        "Welcome to the Ariel CS 2026 Bot.\n\n"
        "This bot helps Computer Science students with:\n"
        "📚 Answering questions about course materials\n"
        "🔍 Solving math problems from images\n\n"
        "Use /help to see available commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command"""
    help_text = """
🤖 *Ariel CS 2026 Bot - Help*

*Commands:*
/start - Start the bot
/help - Show this help message

*Features:*
• Ask questions about course materials
• Upload images of math problems for solutions
• Get answers with source citations

More features coming soon!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


def main():
    """Start the bot in polling mode"""
    if not settings.TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not found in environment variables!")
        logger.error("Please create a .env file based on .env.example")
        return

    logger.info("Creating bot application...")
    application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Start polling
    logger.info("Bot is running in polling mode...")
    logger.info("Press Ctrl+C to stop the bot")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
