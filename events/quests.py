import random
from vkbottle.bot import MessageEvent

import keyboard
import data
from bot import bot

quests = {
    1: {
        "description": "Подписаться на КриптоДеда:\nhttps://vk.com/crypto_ded",
        "group_id": 149147537,
        "reward": 100000
    },
    2: {
        "description": "Подписаться на Soviet Girls:\nhttps://vk.com/sovietgirls_nft",
        "group_id": 220643723,
        "reward": 100000
    },
}

# Обработка команды "💛 Задания""
async def message(event: MessageEvent):
    user_id = event.object.peer_id
    bot_message = "💛 Доступные задания:"

    completed_quests = await data.get_quests(user_id)

    awavailable_quests = 0
    for quest_id, quest in quests.items():
        if quest_id in completed_quests:
            continue
        # делим на разряды
        reward = "{:,}".format(quest["reward"]).replace(",", " ")
        bot_message += f"\n\n🔹 {quest['description']}\n🎁 Награда: {reward} SG₽"
        awavailable_quests += 1

    if awavailable_quests == 0:
        bot_message = "🤯 Все задания выполнены! Скоро появятся новые."


    await bot.api.messages.send(
        user_id=user_id,
        message=bot_message,
        keyboard=keyboard.get_quest_keyboard(),
        random_id=random.randint(0, 2 ** 64),
        dont_parse_links=True
    )
    await event.show_snackbar("💛 Задания")


# Обработка команды "🔹 Проверить выполнение"
async def check(event: MessageEvent):
    user_id = event.object.peer_id
    completed_quests = await data.get_quests(user_id)

    count = 0
    reward_sum = 0
    for quest_id, quest in quests.items():
        if quest_id in completed_quests:
            continue
        if await bot.api.groups.is_member(user_id=user_id, group_id=quest["group_id"]):
            await data.add_quest(user_id, quest_id)
            await data.change_score(user_id, quest["reward"])
            count += 1
            reward_sum += quest["reward"]

    if count == 0:
        bot_message = "🤯 Вы не выполнили ни одного задания."
    else:
        bot_message = f"🎉 Заданий выполнено: {count}! Получено {reward_sum} SG₽."

    await bot.api.messages.send(
        user_id=user_id,
        message=bot_message,
        random_id=random.randint(0, 2 ** 64)
    )
