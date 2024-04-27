import random

from vkbottle.bot import Message
from bot import bot

import data

async def send(message: Message):
    users = data.donuts
    wallets = []
    for user_id in users:
        wallet = await data.get_wallet(user_id)
        wallets.append(wallet)

    bot_message = '\n'.join(wallets)
    await bot.api.messages.send(
        peer_id=message.peer_id,
        message=bot_message,
        random_id=random.randint(0, 2 ** 64)
    )