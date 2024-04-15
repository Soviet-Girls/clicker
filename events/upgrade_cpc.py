import asyncio
from vkbottle.bot import MessageEvent

import data
from  events.upgrades import message as upgrades_message

# Обработка команды "🔼 Улучшение клика"
async def message(event: MessageEvent):
    user_id = event.object.peer_id
    level = await data.get_level(user_id)
    price, income = data.price_count(level)
    score = await data.get_score(user_id)
    if score < price:
        await event.show_snackbar("🛑 Недостаточно средств!")
        return
    try:
        await data.change_score(user_id, -price)
    except Exception as e:
        await event.show_snackbar("🛑 Слишком быстро!")
        raise e
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
    await event.show_snackbar("🔼 Улучшение произведено!")
    await upgrades_message(event)