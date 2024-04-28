import random
from vkbottle.bot import MessageEvent

import data
from bot import bot

# Обработка команды "👥 Пригласить"
async def message(event: MessageEvent):
    user_id = event.object.peer_id
    count = await data.get_ref_count(user_id)
    link = f"https://vk.me/soviet_clicker?ref={user_id}"
    bot_message = "👥 Отправь пригласительную ссылку друзьям, чтобы получить бонус 20 000 SG₽ за каждого друга!\n\n"
    bot_message += "Также ты будешь получать бонусный 5% от добычи твоих друзей (он не будет отниматься у друзей).\n\n"
    bot_message += f"🧮 Приглашено друзей: {count}\n\n"
    bot_message += f"🔗 {link}"
    await bot.api.messages.send(
        user_id=user_id,
        message=bot_message,
        random_id=random.randint(0, 2 ** 64)
    )
    await event.show_snackbar("👥 Реферальная ссылка готова")
