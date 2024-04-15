import random
from vkbottle.bot import MessageEvent

import data
from bot import bot

# Обработка команды "🔝 Топ игроков"
async def message(event: MessageEvent):
    top = await data.get_top()
    bot_message = "🏆 Топ 5 игроков:\n\n"
    for i, user in enumerate(top):
        score = "{:,}".format(user[1]).replace(",", " ")
        user = await bot.api.users.get(user_ids=user[0])
        user = user[0]
        name = user.first_name + " " + user.last_name[0] + "."
        bot_message += f"{i+1}. {name} - {score} SG₽\n"
    await bot.api.messages.send(
        user_id=event.object.peer_id,
        message=bot_message,
        random_id=random.randint(0, 2 ** 64)
    )
    await event.show_snackbar("🔝 Топ игроков")