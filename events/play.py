import random
from vkbottle.bot import MessageEvent

import logging

from templates import play_message
from bot import bot


# Обработка команды "🎮 Играть"
async def message(event: MessageEvent):
    bot_message, kb = await play_message.generate(event.object.peer_id)
    await bot.api.messages.send(
        user_id=event.object.peer_id,
        message=bot_message,
        keyboard=kb,
        random_id=random.randint(0, 2 ** 64)
    )
    await event.show_snackbar("🎮 Игра началась!")
    logging.info(f"[PLAY] Game started! https://vk.com/gim225507433?sel={event.object.peer_id}")