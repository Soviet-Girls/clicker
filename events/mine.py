import asyncio
import random
import time

from vkbottle.bot import MessageEvent

import data
from bot import bot
from templates import play_message

first_clicks = {}
refresh_message = {}
# Обработка команды "🪙 ДОБЫТЬ!"
async def message(event: MessageEvent):
    user_id = event.object.peer_id
    tm_last = await data.get_last_mine(user_id)
    tm = int(time.time())
    first_click = first_clicks.get(user_id, -1)
    if first_click == -1:
        first_clicks[user_id] = tm
        first_click = tm
    tm_diff = tm - tm_last
    sleep_time = data.get_sleep_time()
    _st = 1 if sleep_time == 0 else sleep_time
    if tm_diff < _st:
        egg = random.randint(0, 15)
        if egg == 0:
            await event.show_snackbar("⚡ Вы постите слишком быстро!")
        elif egg == 1:
            await event.show_snackbar("🛑 Куда гонишь, брат?")
        elif egg == 2:
            await event.show_snackbar("🛑 Притормози, родной")
        elif egg == 3:
            await event.show_snackbar("🌿 Сходи потрогай траву")
        else:
            await event.show_snackbar("🛑 Слишком быстро!")
        return
    cpc = await data.get_cpc(user_id)
    try:
        automine_status = await data.get_automine_status(user_id)
        if tm_diff > 600:
            if automine_status:
                new_cpc = int(tm_diff /2 * cpc / 100)
                if new_cpc > 10000:
                    new_cpc = 10000
                elif new_cpc < 1:
                    new_cpc = 1
                cpc += new_cpc
            first_clicks[user_id] = tm
            first_click = tm
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
        if tm - first_click > 1200:
            await event.show_snackbar("⌛ Отвлекись на 10 минут")
            return
        await data.change_score(user_id, cpc)
        await data.set_last_mine(user_id, tm)
    except Exception as e:
        await event.show_snackbar("🛑 Слишком быстро!")
        raise e
    score = await data.get_score(user_id)
    _rm = refresh_message.get(user_id, 0)
    try:
        await event.show_snackbar(f"💸 {score} (+{cpc})")
    except Exception as e:
        print(f"Error showing snackbar: {e}")
        await asyncio.sleep(4)
        await event.show_snackbar(f"💸 {score} (+{cpc})")
    try:
        if _rm == 4:
            bot_message, kb = await play_message.generate(event.object.peer_id, score)
            await bot.api.messages.edit(
                peer_id=event.object.peer_id,
                conversation_message_id=event.conversation_message_id,
                message=bot_message,
                keyboard=kb,
                random_id=random.randint(0, 2 ** 64)
            )
            _rm = 0
        else:
            _rm += 1
        refresh_message[user_id] = _rm

    except Exception as e:
        print(f"Error editing message: {e}")