import random

from vkbottle.bot import Message
from bot import bot

import data

async def send(message: Message):
    users = data.donuts
    for user_id in users:
        try:
            await data.change_score(user_id, 500000)
            await bot.api.messages.send(
                peer_id=user_id,
                message="🎉 Вам начислен бонус 1 000 000 SG₽",
                random_id=random.randint(0, 2 ** 64)
            )
        except:
            pass
    await message.answer("Бонус начислен всем донам сообщества")