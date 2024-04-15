import random
from vkbottle import Keyboard, OpenLink, Callback, VKPay

import data

def get_play_keyboard(rocket: bool = False, secret_code: int = 0):
    keyboard = Keyboard(inline=True)
    if rocket:
        position = random.choice([0, 1, 2, 3])
        if position == 0:
            keyboard.add(Callback("🚀 БОНУС!", payload={"command": f"rocket-{secret_code}"}))
            keyboard.row()
            keyboard.add(Callback("💰 ДОБЫТЬ!", payload={"command": "mine"}))
        elif position == 1:
            keyboard.add(Callback("💰 ДОБЫТЬ!", payload={"command": "mine"}))
            keyboard.add(Callback("🚀 БОНУС!", payload={"command": f"rocket-{secret_code}"}))
        elif position == 2:
            keyboard.add(Callback("🚀 БОНУС!", payload={"command": f"rocket-{secret_code}"}))
            keyboard.add(Callback("💰 ДОБЫТЬ!", payload={"command": "mine"}))
        elif position == 3:
            keyboard.add(Callback("💰 ДОБЫТЬ!", payload={"command": "mine"}))
            keyboard.row()
            keyboard.add(Callback("🚀 БОНУС!", payload={"command": f"rocket-{secret_code}"}))
    else:
        keyboard.add(Callback("💰 ДОБЫТЬ!", payload={"command": "mine"}))
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
    keyboard.add(Callback("🖼️ Получить NFT", payload={"command": "whitelist"}))
    keyboard.add(OpenLink(label="📖 Инструкция", link="https://vk.com/wall-225507433_2"))
    return keyboard

async def get_upgrades_keyboard(user_id: int):
    keyboard = Keyboard(inline=True)
    level = await data.get_level(user_id)
    cpc_upgrade_price, _ = data.price_count(level)
    cpc_upgrade_price = "{:,}".format(cpc_upgrade_price).replace(",", " ")
    if level < 121:
        keyboard.add(Callback(f"🔼 Улучшение клика за {cpc_upgrade_price} SG₽", payload={"command": "upgrade_cpc"}))
    automine_status = await data.get_automine_status(user_id)
    if automine_status is False:
        keyboard.row()
        keyboard.add(Callback("🤖 Автодобыча, 5000 SG₽", payload={"command": "upgrade_automine"}))
    if level < 121:
        keyboard.row()
    keyboard.add(Callback("🎰 Мне повезет, 1000 SG₽", payload={"command": "casino"}))
    return keyboard

def get_pay_keyboard():
    keyboard = Keyboard(inline=True)
    keyboard.add(VKPay(payload={'pays': 0}, hash="action=transfer-to-group&group_id=225507433&aid=1"))
    return keyboard