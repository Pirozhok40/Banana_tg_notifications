import re
import sys
import locale

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from database import add_item, get_items, delete_item, update_notification_status, save_chat_id, get_chat_id
from steam_api import fetch_price
from config import NOTIFICATION_MODE

sys.stdout.reconfigure(encoding='utf-8')  # Настраиваем вывод Python на UTF-8
locale.setlocale(locale.LC_ALL, 'C.UTF-8')  # Устанавливаем локаль на UTF-8

# Состояния для ConversationHandler
INPUT_NAME, INPUT_PRICE = range(2)

# Константы для состояния
STATE_CHANGE_INTERVAL = "change_interval"
STATE_CHANGE_MODE = "change_mode"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Стартовая команда, которая сохраняет ID чата и открывает главное меню"""
    chat_id = update.effective_chat.id
    context.user_data["chat_id"] = chat_id
    await update.message.reply_text("Добро пожаловать в бот отслеживания цен!")
    await main_menu(update, context)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Главное меню с кнопками"""
    keyboard = [
        ["Добавить предмет", "Удалить предмет"],
        ["Список предметов", "Настройки"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("📋 Главное меню. Выберите действие:", reply_markup=reply_markup)


async def process_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка выбора действия из меню"""
    text = update.message.text.strip()

    if text == "Добавить предмет":
        await update.message.reply_text("Введите название предмета или ссылку:")
        context.user_data["state"] = "add_item_name"


    elif text == "Удалить предмет":

        items = get_items()

        if not items:
            await update.message.reply_text("Список отслеживаемых предметов пуст.")

            return

        # Формируем кнопки для каждого предмета

        keyboard = [

            [InlineKeyboardButton(f"{name} ❌", callback_data=f"delete_{name}")]

            for name, _, _ in items

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Выберите предмет для удаления:", reply_markup=reply_markup)

    elif text == "Список предметов":
        items = get_items()
        if not items:
            await update.message.reply_text("Список отслеживаемых предметов пуст.")
            return

        item_list = "\n".join(f"- {name}: {price} руб." for name, price, _ in items)
        await update.message.reply_text(f"📜 Отслеживаемые предметы:\n{item_list}")

    elif text == "Настройки":
        keyboard = [
            ["Изменить интервал проверки", "Изменить режим уведомлений"],
            ["Вернуться в главное меню"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("⚙️ Настройки. Выберите параметр для изменения:", reply_markup=reply_markup)

    elif text == "Изменить интервал проверки":
        await update.message.reply_text("Введите новый интервал проверки в секундах:")
        context.user_data["state"] = "change_interval"

    elif text == "Изменить режим уведомлений":
        await update.message.reply_text("Введите режим уведомлений (always или once):")
        context.user_data["state"] = "change_mode"

    elif text == "Вернуться в главное меню":
        await main_menu(update, context)

    else:
        await update.message.reply_text("Неизвестная команда. Пожалуйста, выберите действие из меню.")


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка сообщений в зависимости от текущего состояния"""
    state = context.user_data.get("state")

    if state == "add_item_name":
        # Логика добавления предмета
        text = update.message.text.strip()
        if text.startswith("https://steamcommunity.com/market/listings/"):
            match = re.search(r"listings/\d+/([^/]+)$", text)
            if match:
                item_name = match.group(1)
            else:
                await update.message.reply_text("Некорректная ссылка. Попробуйте снова.")
                return
        else:
            item_name = text

        context.user_data["item_name"] = item_name
        context.user_data["state"] = "add_item_price"
        await update.message.reply_text(f"Название: {item_name}. Теперь введите целевую цену (например, 0.04):")

    elif state == "add_item_price":
        # Логика добавления цены
        try:
            target_price = float(update.message.text.strip())
            item_name = context.user_data.get("item_name")
            if not item_name:
                await update.message.reply_text("Ошибка: название предмета не найдено. Попробуйте снова.")
                context.user_data["state"] = None
                return

            add_item(item_name, target_price)

            # Отправляем сообщение о добавлении/обновлении
            await update.message.reply_text(f"✅ Предмет '{item_name}' добавлен с ценой {target_price} руб.")
            context.user_data["state"] = None
            await start(update, context)  # Возвращаемся в главное меню
        except ValueError:
            await update.message.reply_text("Ошибка: введите корректное число.")

    elif state == "change_interval":
        # Изменение интервала проверки
        try:
            new_interval = int(update.message.text.strip())
            context.user_data["state"] = None
            await update.message.reply_text(f"Интервал проверки установлен на {new_interval} секунд.")
        except ValueError:
            await update.message.reply_text("Ошибка: введите корректное число.")

    elif state == "change_mode":
        # Изменение режима уведомлений
        mode = update.message.text.strip().lower()
        if mode in ["always", "once"]:
            context.user_data["state"] = None
            await update.message.reply_text(f"Режим уведомлений установлен на '{mode}'.")
        else:
            await update.message.reply_text("Ошибка: выберите 'always' или 'once'.")

    else:
        await update.message.reply_text("Неизвестное действие. Вернитесь в меню: /start")


async def check_prices(context) -> None:
    """Проверяет цены предметов и отправляет уведомления"""
    chat_id = get_chat_id()
    if not chat_id:
        print("[DEBUG] CHAT_ID не найден. Уведомления не отправляются.")
        return  # Если chat_id не сохранён, проверка не выполняется

    items = get_items()
    if not items:
        print("[DEBUG] Нет предметов для проверки.")
        return

    print(f"[DEBUG] Проверяем предметы: {items}")

    for item_name, target_price, notified in items:
        current_price = fetch_price(item_name)

        if current_price is None:
            print(f"[DEBUG] Не удалось получить цену для '{item_name}'.")
            continue

        print(f"[DEBUG] Проверяем '{item_name}': текущая цена {current_price}, целевая {target_price}, статус {notified}")

        if current_price >= target_price:
            if NOTIFICATION_MODE == "always" or (NOTIFICATION_MODE == "once" and not notified):
                # Отправляем уведомление
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⚠️ Цена на '{item_name}' достигла {current_price} руб. или выше (целевая: {target_price} руб.)."
                )
                print(f"[DEBUG] Уведомление отправлено для '{item_name}'.")
                if NOTIFICATION_MODE == "once":
                    update_notification_status(item_name, True)
        elif notified and NOTIFICATION_MODE == "once":
            # Сбрасываем статус уведомления
            update_notification_status(item_name, False)
            print(f"[DEBUG] Сброшен статус уведомления для '{item_name}'.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отмена текущей команды"""
    context.user_data["state"] = None
    await start(update, context)  # Возвращаемся в главное меню


async def save_user_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сохраняет chat_id пользователя"""
    chat_id = update.effective_chat.id
    save_chat_id(chat_id)
    await update.message.reply_text("📋 Добро пожаловать! Ваш chat_id сохранён.")


async def delete_item_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вывод списка предметов для удаления в виде кнопок"""
    items = get_items()
    if not items:
        await update.message.reply_text("Список отслеживаемых предметов пуст.")
        return

    # Формируем клавиатуру с кнопками для каждого предмета
    keyboard = [
        [
            InlineKeyboardButton(f"{name} ❌", callback_data=f"delete_{name}")
        ]
        for name, _, _ in items
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите предмет для удаления:", reply_markup=reply_markup)


async def handle_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка нажатий на кнопки удаления"""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("delete_"):
        item_name = query.data.split("_", 1)[1]
        deleted = delete_item(item_name)

        if deleted:
            await query.edit_message_text(f"✅ Предмет '{item_name}' успешно удалён.")
        else:
            await query.edit_message_text(f"❌ Предмет '{item_name}' не найден.")
