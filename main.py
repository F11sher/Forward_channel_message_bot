import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware

from loguru import logger

from core.handlers.basic import get_start, get_mailed_message
from core.settings import settings
from core.utils.commands import set_commands


@logger.catch
async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, text='Admin message: <b>Бот запущен!</b> ')
    logger.info(f'Bot start by Admin:{settings.bots.admin_id}')


@logger.catch
async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text='Admin message: <b>Бот отключен!</b>')
    logger.info(f'Bot stop by Admin:{settings.bots.admin_id}')


@logger.catch
async def start():
    logger.add(
        'logs/debug.log',
        format="{time} {level} {message}",
        level="DEBUG",
        rotation="1 week",
        compression="zip"
    )

    bot = Bot(token=settings.bots.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware.register(ChatActionMiddleware())

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.message.register(get_start, Command(commands=['start']), flags={'chat_action': 'typing'})

    dp.channel_post.register(get_mailed_message,
                             F.chat.id == -1002290641730,
                             flags={'chat_action': 'typing'})

    try:
        await dp.start_polling(bot)

    except:
        logger.error(f'Bot start error.')

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
