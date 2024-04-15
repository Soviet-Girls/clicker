import random
from vkbottle.bot import MessageEvent

import keyboard
from bot import bot

# Обработка команды "🛍️  Улучшения"
async def message(event: MessageEvent):
    user_id = event.object.peer_id
    bot_message = "Выбери улучшение:"
    await bot.api.messages.send(
        user_id=user_id,
        message=bot_message,
        keyboard=await keyboard.get_upgrades_keyboard(user_id),
        random_id=random.randint(0, 2 ** 64)
    )
    await event.show_snackbar("🛍️ Улучшения")