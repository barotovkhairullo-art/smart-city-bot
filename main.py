import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота (замените на ваш)
API_TOKEN = 'YOUR_BOT_TOKEN'

# ID админа (замените на ваш реальный ID)
ADMIN_ID = 123456789  # Здесь должен быть ваш цифровой ID в Telegram

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для получения информации о группе
async def get_group_info(group_id: int) -> str:
    try:
        chat = await bot.get_chat(group_id)
        group_name = chat.title or "Без названия"
        group_type = "Группа" if chat.type == "group" else "Супергруппа" if chat.type == "supergroup" else "Канал"
        members_count = await bot.get_chat_members_count(group_id)
        
        return f"📋 {group_name}\n🆔 ID: {group_id}\n👥 Тип: {group_type}\n👥 Участников: {members_count}"
    except Exception as e:
        return f"🆔 ID группы: {group_id}\n❌ Не удалось получить информацию: {e}"

# Функция для отправки уведомления админу при запуске
async def on_startup():
    try:
        await bot.send_message(ADMIN_ID, "✅ Сервер бота запущен и работает!")
        logging.info("Уведомление отправлено админу")
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления админу: {e}")

# Функция для отправки уведомления админу при остановке
async def on_shutdown():
    try:
        await bot.send_message(ADMIN_ID, "❌ Сервер бота остановлен!")
        logging.info("Уведомление об остановке отправлено админу")
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления об остановке: {e}")

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для умного города. Используй /help для списка команд.")

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = """
Доступные команды:
/start - Начать работу
/help - Показать справку
/worktime - Узнать время работы
/contacts - Контакты администрации
/groups - Информация о группах (только для админа)
"""
    await message.answer(help_text)

# Обработчик команды /worktime
@dp.message(Command("worktime"))
async def cmd_worktime(message: types.Message):
    await message.answer("🕐 Время работы: 8:00 - 17:00")

# Обработчик команды /contacts
@dp.message(Command("contacts"))
async def cmd_contacts(message: types.Message):
    contacts_text = """
📞 Контакты администрации:

📍 Адрес: г. Умный Город, ул. Центральная, 1
📞 Телефон: +7 (999) 123-45-67
📧 Email: admin@smartcity.gov
🌐 Сайт: www.smartcity.gov
"""
    await message.answer(contacts_text)

# Обработчик команды /groups (только для админа)
@dp.message(Command("groups"))
async def cmd_groups(message: types.Message):
    # Проверяем, является ли пользователь админом
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Эта команда доступна только администратору.")
        return
    
    # Здесь должны быть ID ваших групп (замените на реальные)
    group_ids = [-1001234567890, -1009876543210]  # Пример ID групп
    
    groups_info = "📊 **Информация о группах:**\n\n"
    
    for i, group_id in enumerate(group_ids, 1):
        group_info = await get_group_info(group_id)
        groups_info += f"{i}. {group_info}\n\n"
    
    await message.answer(groups_info, parse_mode="Markdown")

# Обработчик текстовых сообщений
@dp.message()
async def echo_message(message: types.Message):
    await message.answer("Извините, я не понимаю ваше сообщение. Используйте /help для списка команд.")

# Основная функция
async def main():
    # Отправляем уведомление админу при запуске
    await on_startup()
    
    # Запускаем бота
    await dp.start_polling(bot)
    
    # При остановке бота отправляем уведомление
    await on_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")
