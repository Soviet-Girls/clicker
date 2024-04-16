import random
from vkbottle.bot import MessageEvent

import logging

import keyboard
import data
from bot import bot

# Загружаем задания из жсон файла в корне проекта
import json

def load_quests():
    with open("quests.json", "r") as file:
        quests = json.load(file)
    return quests

# Обработка команды "💛 Задания""
async def message(event: MessageEvent):
    await event.show_snackbar("💛 Задания")
    user_id = event.object.peer_id
    bot_message = "💛 Доступные задания:"
    quests = load_quests()

    completed_quests = await data.get_quests(user_id)

    awavailable_quests = 0
    for quest_id, quest in quests.items():
        quest_id = int(quest_id)
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
            random_id=random.randint(0, 2 ** 64),
            dont_parse_links=True
        )
        return


    await bot.api.messages.send(
        user_id=user_id,
        message=bot_message,
        keyboard=keyboard.get_quest_keyboard(),
        random_id=random.randint(0, 2 ** 64),
        dont_parse_links=True
    )


# Обработка команды "🔹 Проверить выполнение"
async def check(event: MessageEvent):
    user_id = event.object.peer_id
    completed_quests = await data.get_quests(user_id)
    quests = load_quests()
    count = 0
    reward_sum = 0
    for quest_id, quest in quests.items():
        quest_id = int(quest_id)
        if quest_id in completed_quests:
            continue
        if await bot.api.groups.is_member(user_id=user_id, group_id=quest["group_id"]):
            await data.add_quest(user_id, quest_id)
            await data.change_score(user_id, quest["reward"])
            count += 1
            reward_sum += quest["reward"]
            logging.info(f"[QUESTS] Cmpleted quest {quest_id}! https://vk.com/gim225507433?sel={user_id}")

    if count == 0:
        bot_message = "🤯 Вы не выполнили ни одного задания."
    else:
        reward_sum = "{:,}".format(reward_sum).replace(",", " ")
        bot_message = f"🎉 Заданий выполнено: {count}! Получено {reward_sum} SG₽."


    await bot.api.messages.send(
        user_id=user_id,
        message=bot_message,
        random_id=random.randint(0, 2 ** 64)
    )
    await event.answer("🔹 Выполнение проверено")
