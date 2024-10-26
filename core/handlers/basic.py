import json

from aiogram import Bot
from aiogram.types import Message
from loguru import logger

from core.settings import settings


@logger.catch
async def get_start(message: Message, bot: Bot):
    user_id = str(message.from_user.id)

    with open('users_data.json', 'r') as file:
        current_users = json.load(file)

    if user_id not in list(current_users.keys()) or not current_users[user_id]:
        current_users[user_id] = True
        print(current_users)

        with open('users_data.json', 'w', encoding='utf-8') as j_file:
            json.dump(current_users, j_file, indent=4)

        await bot.send_message(user_id, 'Вы подписаны на рассылку!')
        logger.info(f'Новый пользователь подписан на рассылку: {message.from_user.username}({user_id})')
        await bot.send_message(settings.bots.admin_id, 'Новый пользователь подписался на рассылку:\n'
                                                       f'ID: {user_id}\n'
                                                       f'Username: {message.from_user.username}')


@logger.catch
async def get_mailed_message(message: Message, bot: Bot):
    logger.debug(f'Получено новое сообщение в группе: {message.chat.username}({message.chat.id})')
    with open('users_data.json', 'r') as file:
        current_users = json.load(file)

    success_mail = 0
    error_mail = 0
    for user in current_users:
        if current_users[user]:
            try:
                await bot.forward_message(int(user), message.chat.id, message.message_id)
                success_mail += 1

            except Exception as ex:
                logger.warning(f'Пользователь {current_users[user]}({user}) заблокировал бота :(')
                current_users[user] = False
                error_mail += 1

    logger.debug(f'Рассылка завершена! Результат:\n'
                 f'Успешных пересылок: {success_mail}\n'
                 f'Пользователи, заблокировавшие бота: {error_mail}')

    with open('users_data.json', 'w', encoding='utf-8') as j_file:
        json.dump(current_users, j_file, indent=4)
