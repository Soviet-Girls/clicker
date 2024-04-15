import asyncio
from vkbottle.bot import MessageEvent

import data
from  events.upgrades import message as upgrades_message

# Обработка команды "🤖 Автодобыча"
async def message(event: MessageEvent):
    user_id = event.object.peer_id
    score = await data.get_score(user_id)
    if score < 5000:
        await event.show_snackbar("🛑 Недостаточно средств!")
        return
    try:
        await data.change_score(user_id, -5000)
    except Exception as e:
        await event.show_snackbar("🛑 Слишком быстро!")
        raise e
    _i = 0
    while True:
        try:
            await data.automine_on(user_id)
            break
        except Exception as e:
            _i += 1
            if _i > 5:
                raise e
            await asyncio.sleep(1)
    await event.show_snackbar("🤖 Автодобыча включена!")
    await upgrades_message(event)