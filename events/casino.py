
import random
import asyncio
from vkbottle.bot import MessageEvent

import logging

import data

# Обработка команды "🎰 Казино"
async def message(event: MessageEvent):
    user_id = event.object.peer_id
    score = await data.get_score(user_id)
    if score < 1000:
        await event.show_snackbar("🛑 Недостаточно средств!")
        logging.info(f"[CASINO] Not enough money! https://vk.com/gim225507433?sel={user_id}")
        return
    await data.change_score(user_id, -1000)
    prize = random.randint(0, 1000)
    if prize == 0:
        await data.change_score(user_id, 100000)
        user_id = event.object.peer_id
        level = await data.get_level(user_id)
        price, income = data.price_count(level)
        _i = 0
        while True:
            try:
                await data.change_cpc(user_id, income)
                break
            except Exception as e:
                _i += 1
                if _i > 5:
                    raise e
                await asyncio.sleep(1)
        _i = 0
        while True:
            try:
                await data.upgrade_level(user_id)
                break
            except Exception as e:
                _i += 1
                if _i > 5:
                    raise e
                await asyncio.sleep(1)
        await event.show_snackbar("🎉 Джекпот! Вы выиграли 100 000 SG₽ и улучшение клика!")
        logging.info(f"[CASINO] Jackpot! https://vk.com/gim225507433?sel={user_id}")
    elif prize < 50:
        await data.change_score(user_id, 10000)
        await event.show_snackbar("🎉 Вы выиграли 10 000 SG₽!")
        logging.info(f"[CASINO] 10 000 SG₽! https://vk.com/gim225507433?sel={user_id}")
    elif prize < 100:
        await data.change_score(user_id, 1000)
        await event.show_snackbar("🎉 Вы выиграли 1 000 SG₽!")
        logging.info(f"[CASINO] 1 000 SG₽! https://vk.com/gim225507433?sel={user_id}")
    elif prize < 700:
        await data.change_score(user_id, 500)
        await event.show_snackbar("🎉 Вы выиграли 500 SG₽!")
        logging.info(f"[CASINO] 500 SG₽! https://vk.com/gim225507433?sel={user_id}")
    else:
        await event.show_snackbar("😢 Вы ничего не выиграли")
        logging.info(f"[CASINO] Nothing! https://vk.com/gim225507433?sel={user_id}")