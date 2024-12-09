# Banana_tg_notifications Bot 🎮

Этот бот отслеживает цены на предметы в игре Banana в Steam и отправляет уведомления в Telegram, когда цена достигает или превышает заданную.

## 📋 Функциональность

- **Добавление предметов для отслеживания**: Укажите название предмета или ссылку из Steam Marketplace и целевую цену.
- **Удаление предметов**: Удаляйте предметы из списка отслеживания через удобное меню.
- **Список предметов**: Отображает все добавленные предметы с их текущими целевыми ценами.
- **Настройки**: 
  - Изменение интервала проверки цен.
  - Выбор режима уведомлений: одноразово или после каждой проверки.
- **Интерактивное меню**: Простая и интуитивная навигация через кнопки.

## 🚀 Установка и запуск

### 1. Требования
- Python 3.10+
- Активный токен Telegram-бота. [Как получить токен] (https://core.telegram.org/bots#6-botfather).

### 2. Клонирование репозитория
git clone https://github.com/Pirozhok40/Banana_tg_notifications

cd Banana_tg_notifications

### 3. Установка зависимостей
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

### 4. Настройка токена в config.py
TELEGRAM_TOKEN = 

### 5. Запуск
python3 bot.py

🛠 Структура проекта

├── bot.py                 # Главный файл бота

├── commands.py            # Обработка команд и меню

├── database.py            # Управление базой данных

├── steam_api.py           # Взаимодействие с API Steam

├── config.py              # Конфигурационные параметры

├── requirements.txt       # Список зависимостей

└── README.md              # Описание проекта

💡 Настройка
Интервал проверки цен
Настраивается в config.py:

CHECK_INTERVAL = 60  # Интервал проверки в секундах

Режим уведомлений
Выберите:
"once" — уведомлять один раз при достижении целевой цены.
"always" — уведомлять при каждой проверке.
Настройка также выполняется через меню настроек бота.

🤝 Вклад
Если вы хотите внести вклад в проект:
Сделайте форк репозитория.
Создайте ветку для вашей функции (git checkout -b feature-branch).
Отправьте пул-реквест.
