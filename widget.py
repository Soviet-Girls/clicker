from vkbottle.bot import Bot

import config
import data

bot = Bot(config.VK_WIDGET)


async def generate_code():
    # виджет топ 5
    top = await data.get_top()
    users = await bot.api.users.get(user_ids=[user[0] for user in top])
    names = [f"{user.first_name} {user.last_name[0]}." for user in users]
    users = []
    emojis = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(top):
        users.append({
            "top": emojis[i] if i < 3 else '🏅',
            "id": user[0],
            "score": user[1],
            "name": names[i]
        })

    widget = {
        "title": "🏆 Топ 5 игроков",
        "title_url": "https://vk.me/soviet_clicker",
        "more": "Играть",
        "more_url": "https://vk.me/soviet_clicker",
        "head": [{
            "text": "Место"
        }, {
            "text": "Имя",
            "align": "center"
        }, {
            "text": "Баланс",
            "align": "center"
        }],
        "body": [
            [{
                "text": str(user["top"])
            }, {
                "text": user["name"],
                "align": "center"
            }, {
                "text": str(user["score"]),
                "align": "center"
            }] for user in users
            ]
    }
    return widget

async def update():
    code = await generate_code()
    await bot.api.app_widgets.update(code=code, type="table")