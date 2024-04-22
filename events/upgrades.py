import random
from vkbottle.bot import MessageEvent

import keyboard
import data
from bot import bot

# Обработка команды "🛍️  Улучшения"
async def message(event: MessageEvent):
    user_id = event.object.peer_id
    level = await data.get_level(user_id)
    price, income = data.price_count(level)
    bot_message = f'📊 Уровень: {level}\n'
    bot_message += f'На следующем уровне: +{income} SG₽ за клик\n'
    bot_message = "Выбери улучшение:"
    await bot.api.messages.send(
        user_id=user_id,
        message=bot_message,
        keyboard=await keyboard.get_upgrades_keyboard(user_id),
        random_id=random.randint(0, 2 ** 64)
    )
    await event.show_snackbar("🛍️ Улучшения")