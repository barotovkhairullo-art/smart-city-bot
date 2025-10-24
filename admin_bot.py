import json
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from history_events import add_event, get_tajikistan_history, load_events
from weather_service import get_dushanbe_weather

TELEGRAM_BOT_TOKEN = "8249137825:AAHChjPuHOdL7Y5su0gYpQnwtDZ4ubfXsl0"
CHANNEL_ID = "-1003104338746"
STICKER_ID = "CAACAgIAAxkBAAEPnw5o-adhPImHgSmQpfa-yO9kVk1RxAACwwwAAsVEyEtvpOuf2LbHBDYE"

# Загрузка конфигурации
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

def is_admin(user_id):
    config = load_config()
    return user_id in config["ADMIN_IDS"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Доступ запрещен!")
        return
    
    await update.message.reply_text(
        "👑 Панель администратора\n\n"
        "⏰ /time - Текущие настройки\n"
        "🕐 /settime 10 45 - Установить время\n"
        "📅 /addevent 15.11 Событие - Добавить событие\n"
        "📚 /events - Список дат\n"
        "🔧 /settings - Настройки бота\n"
        "📨 /test - Тестовая отправка\n"
        "⚡ /enable - Включить бота\n"
        "🚫 /disable - Выключить бота"
    )

async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Доступ запрещен!")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("❌ Используйте: /settime ЧАС МИНУТА\nПример: /settime 10 45")
        return
    
    try:
        hour = int(context.args[0])
        minute = int(context.args[1])
        
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            config = load_config()
            config["SEND_HOUR"] = hour
            config["SEND_MINUTE"] = minute
            save_config(config)
            
            await update.message.reply_text(f"✅ Время установлено на {hour:02d}:{minute:02d}")
        else:
            await update.message.reply_text("❌ Неверное время! Часы: 0-23, Минуты: 0-59")
    except:
        await update.message.reply_text("❌ Ошибка! Используйте числа")

async def add_event_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Доступ запрещен!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("❌ Используйте: /addevent ДД.ММ Событие\nПример: /addevent 15.11 1990 – Событие")
        return
    
    try:
        date_str = context.args[0]
        event_text = ' '.join(context.args[1:])
        day, month = map(int, date_str.split('.'))
        
        result = add_event(month, day, event_text)
        await update.message.reply_text(result)
    except:
        await update.message.reply_text("❌ Ошибка! Формат: ДД.ММ")

async def test_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Доступ запрещен!")
        return
    
    await update.message.reply_text("🔄 Отправляю тестовое сообщение...")
    
    # Отправка стикера
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendSticker"
        data = {"chat_id": CHANNEL_ID, "sticker": STICKER_ID}
        requests.post(url, data=data)
    except:
        pass
    
    # Отправка сообщения
    history_text = get_tajikistan_history()
    weather_text = get_dushanbe_weather()
    
    message = "🔄 ТЕСТОВАЯ ОТПРАВКА\n\n"
    message += history_text + "\n"
    message += weather_text + "\n\n"
    message += "📖 Государственное унитарное предприятие «Умный город»"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHANNEL_ID, "text": message}
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        await update.message.reply_text("✅ Тестовое сообщение отправлено!")
    else:
        await update.message.reply_text("❌ Ошибка отправки")

async def show_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Доступ запрещен!")
        return
    
    events_db = load_events()
    if not events_db:
        await update.message.reply_text("📭 Нет событий в базе")
        return
    
    message = "📚 Даты с событиями:\n\n"
    for date_key in sorted(events_db.keys()):
        month = int(date_key[:2])
        day = int(date_key[2:])
        count = len(events_db[date_key])
        message += f"📅 {day:02d}.{month:02d} - {count} событий\n"
    
    await update.message.reply_text(message)

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Доступ запрещен!")
        return
    
    config = load_config()
    status = "✅ ВКЛЮЧЕН" if config["BOT_ENABLED"] else "❌ ВЫКЛЮЧЕН"
    
    await update.message.reply_text(
        f"⚙️ Настройки бота:\n\n"
        f"⏰ Время отправки: {config['SEND_HOUR']:02d}:{config['SEND_MINUTE']:02d}\n"
        f"🔧 Статус: {status}\n"
        f"👑 Админов: {len(config['ADMIN_IDS'])}"
    )

async def enable_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Доступ запрещен!")
        return
    
    config = load_config()
    config["BOT_ENABLED"] = True
    save_config(config)
    await update.message.reply_text("✅ Бот включен!")

async def disable_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Доступ запрещен!")
        return
    
    config = load_config()
    config["BOT_ENABLED"] = False
    save_config(config)
    await update.message.reply_text("✅ Бот выключен!")

# Создаем бота
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Регистрируем команды
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("settime", set_time))
application.add_handler(CommandHandler("addevent", add_event_cmd))
application.add_handler(CommandHandler("test", test_send))
application.add_handler(CommandHandler("events", show_events))
application.add_handler(CommandHandler("settings", show_settings))
application.add_handler(CommandHandler("enable", enable_bot))
application.add_handler(CommandHandler("disable", disable_bot))