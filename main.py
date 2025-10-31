import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== НАСТРОЙКИ ==========
# Токен бота от @BotFather
API_TOKEN = '8404371791:AAG-uiZ7Oab4udWZsb5HgijR56dPMPBH9W0'

# ID админа (ваш ID в Telegram)
ADMIN_ID = 708267814  # Ваш ID: @bkh3044

# Список ID групп
GROUPS = [
    -1003104338746,  # Группа: "Тест Группа"
]
# ===============================

# Инициализация бота и диспетчера
try:
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    print("✅ Токен валидный, бот инициализирован")
except Exception as e:
    print(f"❌ Ошибка инициализации бота: {e}")
    exit()

# Функция для отправки уведомления админу при запуске
async def on_startup():
    try:
        await bot.send_message(ADMIN_ID, "✅ Сервер бота запущен и работает!")
        logger.info("Уведомление отправлено админу")
        
        # Логируем информацию о группах
        for group_id in GROUPS:
            try:
                chat = await bot.get_chat(group_id)
                group_name = chat.title or "Без названия"
                logger.info(f"📋 Группа: {group_name} | 🆔 ID: {group_id}")
            except Exception as e:
                logger.error(f"Ошибка получения информации о группе {group_id}: {e}")
                
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления админу: {e}")

# Функция для отправки уведомления админу при остановке
async def on_shutdown():
    try:
        await bot.send_message(ADMIN_ID, "❌ Сервер бота остановлен!")
        logger.info("Уведомление об остановке отправлено админу")
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления об остановке: {e}")

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
    
    groups_info = "📊 **Информация о группах:**\n\n"
    
    for i, group_id in enumerate(GROUPS, 1):
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

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    finally:
        # При остановке бота отправляем уведомление
        asyncio.run(on_shutdown())
