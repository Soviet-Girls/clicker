import random
from vkbottle.bot import MessageEvent

import data
from bot import bot
from templates import play_message

# Обработка команды "🚀 БОНУС!"
async def message(event: MessageEvent):
    user_id = event.object.peer_id
    secret_code = await data.get_secret_code(user_id)
    if secret_code == 0:
        await event.show_snackbar("🥲 Код бонуса просрочен")
        return
    elif event.object.payload.get("command") != f"rocket-{secret_code}":
        await event.show_snackbar("🤡 Хорошая попытка")
        return
    else:
        await data.set_secret_code(user_id, 0)
    score = await data.get_score(user_id)
    cpc = await data.get_cpc(user_id)
    bonus = cpc * 5
    try:
        await data.change_score(user_id, bonus)
        await event.show_snackbar(f"🚀 {score} (+{bonus})")
        bot_message, kb = await play_message.generate(user_id)
        await bot.api.messages.edit(
            peer_id=user_id,
            conversation_message_id=event.conversation_message_id,
            message=bot_message,
            keyboard=kb,
            random_id=random.randint(0, 2 ** 64)
        )
    except Exception as e:
        await event.show_snackbar("🛑 Слишком быстро!")
        raise e