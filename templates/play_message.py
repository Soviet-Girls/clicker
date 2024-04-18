import random

import keyboard
import data



async def generate(user_id: int, score: int = -1) -> str:
    if score == -1:
        score = await data.get_score(user_id)
    level = await data.get_level(user_id)
    score = "{:,}".format(score).replace(",", " ")
    bot_message = f"💰 Твой счёт: {score} SG₽"
    bot_message += f"\n📊 Уровень: {level}"
    sleep_time = data.get_sleep_time()
    if sleep_time == 0:
        bot_message += "\n\n⌛ Добыча доступна каждую секунду."
    else:
        bot_message += f"\n\n⌛ Высокая нагрузка! Добыча доступна каждые {sleep_time} секунд."
    wallet = await data.get_wallet(user_id)
    if wallet == "":
        bot_message += "\n\n⚠️ Кошелек Polygon не указан! Отправьте адрес кошелька боту, чтобы получить SG₽ после закрытия игры."
    else:
        wallet = wallet[:5] + "..." + wallet[-5:]
        bot_message += f"\n\n📦 Ваш кошелек: {wallet}.\n После закрытия игры SG₽ будут отправлены на этот адрес."

    rocket = random.randint(0, 20) == 0
    if rocket:
        data.set_secret_code(user_id, random.randint(1000, 9999))
    else:
        data.set_secret_code(user_id, 0)
    kb = keyboard.get_play_keyboard(rocket, data.get_secret_code(user_id))
    return bot_message, kb