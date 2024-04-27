
import time
import random
import asyncio
from vkbottle.bot import MessageEvent

import logging

import data
from bot import bot, user_api

first_clicks = {}
spam_count = {}
# Обработка команды "🎰 Казино"
async def message(event: MessageEvent):
    user_id = event.object.peer_id
    donut = await data.is_donut(user_id)
    tm_last = await data.get_last_mine(user_id)
    tm = int(time.time())
    first_click = first_clicks.get(user_id, -1)
    if first_click == -1:
        first_clicks[user_id] = tm
        first_click = tm

    tm_diff = tm - tm_last
    if tm_diff > 600:
        first_clicks[user_id] = tm
        first_click = tm

    if donut:
        time_ban_diff = 3600
    else:
        time_ban_diff = 1200
    if tm - first_click > time_ban_diff:
        spam_count[user_id] = spam_count.get(user_id, 0) + 1
        if spam_count[user_id] > 50 and not donut:
            await event.show_snackbar(f"⛔ {100-spam_count[user_id]} кликов до бана")
        else:
            await event.show_snackbar("⌛ Отвлекись на 10 минут")
        if spam_count[user_id] > 99 and not donut:
            await user_api.groups.ban(
                group_id=225507433,
                owner_id=user_id,
                reason=0,
                comment="Подозрительная активность. Обратитесь к администору.",
                comment_visible=True
            )
            logging.info(f"[BAN] https://vk.com/gim225507433?sel={user_id}")
            return
        logging.info(f"[SPAM {spam_count[user_id]}/100] https://vk.com/gim225507433?sel={user_id}")
        return

    score = await data.get_score(user_id)
    if score < 1000:
        await event.show_snackbar("🛑 Недостаточно средств!")
        logging.info(f"[CASINO] Not enough money! https://vk.com/gim225507433?sel={user_id}")
        return
    await data.change_score(user_id, -1000)
    prize = random.randint(0, 1000)
    if prize == 0:
        score = await data.change_score(user_id, 100000)
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
        score = "{:,}".format(score).replace(",", " ")
        await event.show_snackbar(f"🎉 Джекпот! Вы выиграли {score} SG₽ и улучшение клика!")
        logging.info(f"[CASINO] Jackpot! https://vk.com/gim225507433?sel={user_id}")
    elif prize < 50:
        score = await data.change_score(user_id, 10000)
        score = "{:,}".format(score).replace(",", " ")
        await event.show_snackbar(f"🎉 Вы выиграли {score} SG₽!")
        logging.info(f"[CASINO] {score} SG₽! https://vk.com/gim225507433?sel={user_id}")
    elif prize < 100:
        score = await data.change_score(user_id, 1000)
        score = "{:,}".format(score).replace(",", " ")
        await event.show_snackbar(f"🎉 Вы выиграли {score} SG₽!")
        logging.info(f"[CASINO] {score} SG₽! https://vk.com/gim225507433?sel={user_id}")
    elif prize < 700:
        score = await data.change_score(user_id, 500)
        score = "{:,}".format(score).replace(",", " ")
        await event.show_snackbar(f"🎉 Вы выиграли {score} SG₽!")
        logging.info(f"[CASINO] {score} SG₽! https://vk.com/gim225507433?sel={user_id}")
    else:
        await event.show_snackbar("😢 Вы ничего не выиграли")
        logging.info(f"[CASINO] Nothing! https://vk.com/gim225507433?sel={user_id}")