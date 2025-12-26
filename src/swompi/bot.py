import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import FSInputFile
from swompi.config import AppConfig
from swompi.session import engine, SessionLocal as db_session_factory
import os
from functions import * 
import tempfile
from storage import FileStorageRepository

config = AppConfig()
storage = FileStorageRepository(config)
API_TOKEN = config.TELEGRAM_BOT_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    with db_session_factory() as db_session:
        add_user(db_session, message.from_user.username or str(message.from_user.id), str(message.chat.id))
        await message.answer("You are registered in the Swompi system")

@dp.message(Command("history"))
async def cmd_history(message: types.Message, command: CommandObject):
    repo_name = command.args
    if not repo_name:
        return await message.answer("Please enter the repository name")
    with db_session_factory() as db_session:    
        result = get_latest_builds_by_repo(db_session, repo_name)
        if not result:
            await message.answer(f"There is no such repository as '{repo_name}'")
        else:            
            await message.answer(result)

@dp.message(Command("status"))
async def cmd_status(message: types.Message, command: CommandObject):
    build_id = command.args
    if not build_id:
        return await message.answer("Please enter the bild_id")

    with tempfile.NamedTemporaryFile(
        mode='wb',  
        prefix=f"build_{build_id}_",
        suffix='.7z',
        dir="/tmp",  
        delete=False
    ) as temp_file:
        file_path = temp_file.name
        await message.answer(f"In progress...")
        success=storage.download_file_to_path(build_id, file_path)
        if not success:
            return await message.answer(f"Failed to upload build {build_id}")
        temp_file.close()
        input_file = FSInputFile(file_path, filename=f"build_{build_id}.7z")
        await message.answer_document(input_file)
    
    os.unlink(file_path)

async def send_build_notification(build_id: int):
    with db_session_factory() as db_session:    
        result = get_build_status(db_session, build_id)
        text = f"result"
        users = session.execute(
                select(User).where(User.chat_id.is_not(None))
            ).scalars().all()
    for user in users:
        await bot.send_message(chat_id, text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
