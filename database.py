import sqlite3

DB_FILE = "database.db"

def init_db() -> None:
    """Инициализация базы данных: создание таблиц при первом запуске"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Создаём таблицу items, если её нет
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            target_price REAL NOT NULL,
            notified INTEGER DEFAULT 0
        )
    """)

    # Создаём таблицу settings, если её нет
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_item(name: str, target_price: float) -> None:
    """Добавление предмета в базу или обновление его цены, если он уже существует."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO items (name, target_price, notified)
        VALUES (?, ?, 0)
        ON CONFLICT(name) DO UPDATE SET target_price = excluded.target_price, notified = 0
    """, (name, target_price))
    conn.commit()
    conn.close()


def get_items() -> list[tuple[str, float, int]]:
    """Получает все предметы из базы данных"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, target_price, notified FROM items")
    items = cursor.fetchall()
    conn.close()
    return items


def delete_item(name: str) -> bool:
    """Удаляет предмет из базы данных по имени"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE name = ?", (name,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def update_notification_status(name: str, notified: bool) -> None:
    """Обновляет статус уведомления для предмета"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE items
        SET notified = ?
        WHERE name = ?
    """, (1 if notified else 0, name))
    conn.commit()
    conn.close()


def save_chat_id(chat_id: int) -> None:
    """Сохраняет или обновляет CHAT_ID в таблице settings."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = ?
    """, ("chat_id", str(chat_id), str(chat_id)))

    conn.commit()
    conn.close()
    

def get_chat_id() -> int | None:
    """Получает chat_id из базы данных"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT value FROM settings WHERE key = 'chat_id'
    """)
    result = cursor.fetchone()
    conn.close()
    return int(result[0]) if result else None
