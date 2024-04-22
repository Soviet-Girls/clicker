import random
from vkbottle.bot import MessageEvent

import data
import keyboard
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

    bot_message = "🏁 Реферальная гонка:\n\n"

    top = await data.get_ref_count_top()
    # Показать топ 5 игроков
    # Если пользователь не в топе, показать его место в конце с сообщением "Вы находитесь на N месте"

    user_in_top = False
    for i, user in enumerate(top):
        count = user[1]
        user = await bot.api.users.get(user_ids=user[0])
        user = user[0]
        name = user.first_name + " " + user.last_name[0] + "."
        bot_message += f"{i+1}. {name} - {count} приглашено\n"
        if user.id == event.object.peer_id:
            user_in_top = True
        if i == 4:
            break
    if not user_in_top:
        for i, user in enumerate(top):
            if user[0] == event.object.peer_id:
                count = user[1]
                bot_message += f"\nВы находитесь на {i+1} месте. Приглашено: {count}.\n"
                break
    await bot.api.messages.send(
        user_id=event.object.peer_id,
        message=bot_message,
        random_id=random.randint(0, 2 ** 64),
        keyboard=keyboard.ref_race_keyboard()
    )

    await event.show_snackbar("🔝 Топ игроков")