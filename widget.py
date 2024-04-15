from vkbottle.bot import Bot

import config
import data

bot = Bot(config.VK_WIDGET)


async def generate_code():
    # виджет топ 5
    users_count = await bot.api.messages.get_conversations(count=1)
    users_count = users_count.count
    top = await data.get_top()
    users = await bot.api.users.get(user_ids=[user[0] for user in top])
    names = [f"{user.first_name} {user.last_name[0]}." for user in users]
    users = []
    emojis = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(top):
        refs = await data.get_ref_count(user[0])
        level = await data.get_level(user[0])
        users.append({
            "top": emojis[i] if i < 3 else '🏅',
            "id": user[0],
            "score": "{:,}".format(user[1]).replace(",", " "),
            "name": names[i],
            "level": level,
            "friends": refs
        })

    widget = {
        "title": f"🏆 Топ 5 игроков (из {users_count})",
        "title_url": "https://vk.me/soviet_clicker",
        "more": "Играть",
        "more_url": "https://vk.me/soviet_clicker",
        "head": [{
            "text": "Имя",
        }, {
            "text": "Баланс",
            "align": "center"
        },
        {   "text": "Уровень",
            "align": "center"
        },
        {
            "text": "Пригласил",
            "align": "right"
        }],
        "body": [
            [{
                "text": user['top'] + ' ' + user["name"],
                "align": "left"
            }, {
                "text": str(user["score"]) + ' SG₽',
                "align": "center"
            },
            {
                "text": str(user["level"]),
                "align": "center"
            },
            {
                "text": str(user["friends"]),
                "align": "right"
            }
            ] for user in users
            ]
    }
    return f"return {widget};"

async def update():
    code = await generate_code()
    await bot.api.app_widgets.update(code=code, type="table")