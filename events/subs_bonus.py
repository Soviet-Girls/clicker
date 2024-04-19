import random

from vkbottle.bot import Message
from bot import bot

import data

async def send(message: Message):
    users = await bot.api.groups.get_members(group_id=225507433)
    for user_id in users.items:
        await data.change_score(user_id, 300000)
        await bot.api.messages.send(
            peer_id=user_id,
            message="🎉 Вам начислен бонус 300 000 SG₽",
            random_id=random.randint(0, 2 ** 64)
        )
    await message.answer("Бонус начислен всем участникам группы")