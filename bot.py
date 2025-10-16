# bot.py

import os
import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import MessageEntityType
from aiogram.types import FSInputFile
from dotenv import load_dotenv

from tools.main_downloader import main_downloader
from tools.exceptions import NoMediaFoundError, DownloadFailedError

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Надішли мені посилання на TikTok, Reels, Pinterest або YT Music, і я завантажу медіа для тебе."
    )


@dp.message(
    F.entity_types.contains(MessageEntityType.URL)
    | F.text.contains("https://")
    | F.text.contains("http://")
)
async def handle_links(message: types.Message):
    processing_message = await message.reply("⏳ Обробляю посилання, зачекайте...")

    url = message.text

    try:
        media_paths = main_downloader(url)

        if not media_paths:
            raise NoMediaFoundError()

        for path in media_paths:
            try:
                file = FSInputFile(path)
                if path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    await message.answer_photo(file)
                elif path.lower().endswith((".mp4", ".mov", ".avi")):
                    await message.answer_video(file)
                elif path.lower().endswith((".mp3", ".wav")):
                    await message.answer_audio(file)
                else:
                    await message.answer_document(file)
            except Exception as e:
                print(f"Помилка при відправці файлу {path}: {e}")
                await message.answer(
                    f"Не вдалося відправити файл: {os.path.basename(path)}"
                )
            finally:
                if os.path.exists(path):
                    os.remove(path)

        await bot.delete_message(
            chat_id=processing_message.chat.id, message_id=processing_message.message_id
        )

    except NoMediaFoundError:
        await processing_message.edit_text(
            "❌ За цим посиланням не знайдено медіафайлів, які можна завантажити."
        )
    except DownloadFailedError as e:
        print(f"Помилка завантаження: {e}")
        await processing_message.edit_text(
            "❌ Сталася помилка під час завантаження. Можливо, контент є приватним або недоступним."
        )
    except Exception as e:
        print(f"Непередбачувана помилка: {e}")
        await processing_message.edit_text(
            "❌ Сталася невідома помилка. Спробуйте інше посилання."
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
