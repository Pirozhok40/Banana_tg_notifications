from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from commands import start, process_menu_selection, process_message, cancel, check_prices, delete_item_menu, handle_delete_callback
from config import TELEGRAM_TOKEN, CHECK_INTERVAL
from database import init_db

def main():

    init_db()

    """Запуск бота"""
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Добавляем задачи
    job_queue = application.job_queue
    # Запускаем проверку цен каждые 60 секунд
    job_queue.run_repeating(check_prices, interval=CHECK_INTERVAL, first=10)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(
        "^(Добавить предмет|Удалить предмет|Список предметов|Настройки|Изменить интервал проверки|Изменить режим уведомлений|Вернуться в главное меню)$"),
                                           process_menu_selection))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("delete", delete_item_menu))
    application.add_handler(CallbackQueryHandler(handle_delete_callback, pattern="^delete_"))

    application.run_polling()

if __name__ == "__main__":
    main()