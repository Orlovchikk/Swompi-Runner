import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import FSInputFile
from swompi.config import AppConfig

from functions import * 

config = AppConfig()
API_TOKEN = config.TELEGRAM_BOT_TOKEN
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
@dp.message(Command("ping"))
async def cmd_ping(message: Message):
    print(f"📨 Получена команда /ping от {message.from_user.id}")
    await message.answer("🏓 Pong! Бот работает!")
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    add_user(db, message.from_user.username or str(message.from_user.id), str(message.chat.id))
    await message.answer("Вы вошли в систему Swompi.")

@dp.message(Command("history"))
async def cmd_history(message: types.Message, command: CommandObject):
    repo_name = command.args
    if not repo_name:
        return await message.answer("Введите название репозитория")
    result = get_latest_builds_by_repo(repo_name )
    if not result:
        await message.answer(f"Нет сборок для репозитория '{repo_name}'")
    else:            
        await message.answer(result)

'''@dp.message(Command("status"))
async def cmd_status(message: types.Message, command: CommandObject):
    build_id = command.args
    if not build_id:
        return await message.answer("Ввидите id сборки: /status <build_id>")

    await message.answer(f" {build_id}...")


    archive_path = f"artifacts/build_{build_id}.7z" '''

async def send_build_notification(chat_id: int, build_id: int):
    result = get_build_status(build_id)
    text = f"result"
    users = session.execute(
            select(User).where(User.chat_id.is_not(None))
        ).scalars().all()
    for user in users:
        await bot.send_message(chat_id, text, parse_mode="Markdown")

async def main():
    print("✅ Бот готов к работе")
    await dp.start_polling(bot)

