import data
from vkbottle import Keyboard, OpenLink, Callback

def get_play_keyboard():
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("🪙 ДОБЫТЬ!", payload={"command": "mine"}))
    return keyboard 

def get_main_keyboard():
    keyboard = Keyboard()
    keyboard.add(Callback("🎮 Играть", payload={"command": "play"}))
    keyboard.row()
    keyboard.add(Callback("🛍️ Улучшения", payload={"command": "upgrades"}))
    keyboard.row()
    keyboard.add(Callback("👥 Пригласить", payload={"command": "ref"}))
    keyboard.add(Callback("🔝 Топ игроков", payload={"command": "top"}))
    keyboard.row()
    keyboard.add(OpenLink(label="📖 Инструкция", link="https://vk.com/wall-225507433_2"))
    return keyboard

async def get_upgrades_keyboard(user_id: int):
    keyboard = Keyboard(inline=True)
    level = await data.get_level(user_id)
    cpc_upgrade_price, _ = data.price_count(level)
    cpc_upgrade_price = "{:,}".format(cpc_upgrade_price).replace(",", " ")
    keyboard.add(Callback(f"🔼 Улучшение клика за {cpc_upgrade_price} SG₽", payload={"command": "upgrade_cpc"}))
    automine_status = await data.get_automine_status(user_id)
    if automine_status is False:
        keyboard.row()
        keyboard.add(Callback("🤖 Автодобыча, 5000 SG₽", payload={"command": "upgrade_automine"}))
    return keyboard