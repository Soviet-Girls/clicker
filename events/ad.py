import asyncio
import random
from vkbottle.bot import Message

from bot import bot

async def send(message: Message):
    if message.from_id != 434356505:
        return
    text = message.text[4:]

    users = await bot.api.messages.get_conversations(count=200)
    all_users = users.items
    for _ in range(users.count // 200):
        offset_multiplier += 1
        users = await bot.api.messages.get_conversations(count=200, offset=offset_multiplier*200)
        # прибавляем к списку новые элементы
        all_users += users.items
    users = all_users

    for user in users:
        _id = user.conversation.peer.id
        try:
            await bot.api.messages.send(
                user_id=_id,
                message='',
                attachment=text,
                random_id=random.randint(0, 2 ** 64)
            )
            await asyncio.sleep(0.5)
        except:
            pass