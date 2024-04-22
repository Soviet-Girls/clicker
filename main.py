import random
import traceback

from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent

import logging

import data
import keyboard
import widget
import events

from rules import CommandRule, WalletRule
from bot import bot

logging.getLogger("vkbottle").setLevel(logging.INFO)

@bot.on.message(text="")
async def blank_message(message: Message):
    if message.from_id != 434356505:
        return
    await message.answer(str(message.json()))

@bot.on.message(CommandRule(["начать", "start", "старт"]))
async def start_message(message: Message):
    await message.answer(
        "Привет! Это бот для добычи Soviet Girls Ruble. Для начала игры нажми на кнопку 🎮 Играть",
        keyboard=keyboard.get_main_keyboard( )
        )
    if message.ref:
        ref = int(message.ref)
        if ref != message.from_id:
            old_ref = await data.get_ref(message.from_id)
            if old_ref != 0:
                return
            await data.set_ref(message.from_id, ref)
            await data.change_ref_count(ref, 1)
            score = await data.change_score(ref, 20000)
            score = "{:,}".format(score).replace(",", " ")
            bot_message = f"🎉 Вы получили {score} SG₽ за приглашение друга!"
            logging.info(f"[REF] {ref} invited {message.from_id}")
            await bot.api.messages.send(
                user_id=ref,
                message=bot_message,
                random_id=random.randint(0, 2 ** 64)
            )

@bot.on.message(CommandRule(["/ref"]))
async def ref_admin_message(message: Message):
    ref = message.ref
    ref_source = message.ref_source
    await message.answer(f"ref: {ref}, ref_source: {ref_source}")


@bot.on.message(CommandRule(["/subs_bonus"]))
async def subs_bonus(message: Message):
    if message.from_id != 434356505:
        return
    await events.subs_bonus.send(message)


banned = []
banned_refresh_count = 0

# Обработка callback
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def callback_handler(event: MessageEvent):
    global banned_refresh_count

    if banned_refresh_count > 99:
        banlist = await bot.api.groups.get_banned(group_id=225507433)
        for user in banlist.items:
            if user.profile.id not in banned:
                banned.append(user.profile.id)
        banned_refresh_count = 0

    if event.object.peer_id in banned:
        logging.info(f"[BANNED] {event.object.peer_id} is banned!")
        return

    if event.object.payload.get("command") == "play":
        await events.play.message(event)
    elif event.object.payload.get("command") == "mine":
        await events.mine.message(event)
    elif event.object.payload.get("command") == "upgrades":
        await events.upgrades.message(event)
    elif event.object.payload.get("command") == "upgrade_cpc":
        await events.upgrade_cpc.message(event)
    elif event.object.payload.get("command") == "upgrade_automine":
        await events.automine.message(event)
    elif event.object.payload.get("command") == "ref":
        await events.ref.message(event)
    elif event.object.payload.get("command") == "top":
        await events.top.message(event)
    elif event.object.payload.get("command") == "casino":
        await events.casino.message(event)
    elif event.object.payload.get("command").startswith("rocket-"):
        await events.bonus.message(event)
    elif event.object.payload.get("command") == "whitelist":
        await events.whitelist.message(event)
    elif event.object.payload.get("command") == "quests":
        await events.quests.message(event)
    elif event.object.payload.get("command") == "check_quest":
        await events.quests.check(event)

    keyboard_version_status = await data.check_keyboard_version(event.object.peer_id)
    if keyboard_version_status is False:
        await bot.api.messages.send(
            message="Клавиатура обновлена!",
            keyboard=keyboard.get_main_keyboard(),
            user_id=event.object.peer_id,
            random_id=random.randint(0, 2 ** 64)
        )
        await data.update_keyboard_version(event.object.peer_id)
    
    banned_refresh_count += 1

# Обработка вступления в группу
@bot.on.raw_event(GroupEventType.GROUP_JOIN)
async def group_join_handler(event):
    # Даём бонус за вступление в группу
    user_id = event['object']['user_id']
    bonus = await data.get_invite_bonus(user_id)
    if bonus is False:
        score = await data.change_score(user_id, 200000)
        score = "{:,}".format(score).replace(",", " ")
        await data.set_invite_bonus(user_id, True)
        try:
            await bot.api.messages.send(
                user_id=user_id,
                message=f"🎉 Вы получили {score} SG₽ за вступление в группу!",
                random_id=random.randint(0, 2 ** 64)
            )
        except Exception as e:
            pass
        logging.info(f"[JOIN] https://vk.com/gim225507433?sel={user_id}")

# Обработка выхода из группы
@bot.on.raw_event(GroupEventType.GROUP_LEAVE)
async def group_leave_handler(event):
    user_id = event['object']['user_id']
    bonus = await data.get_invite_bonus(user_id)
    if bonus is True:
        await data.set_invite_bonus(user_id, False)
        await data.change_score(user_id, -200000)
    try:
        await bot.api.messages.send(
            user_id=user_id,
            message="😢 Вы потеряли бонусные 200 000 SG₽ за выход из группы!",
            random_id=random.randint(0, 2 ** 64)
        )
    except Exception as e:
        pass
    logging.info(f"[LEAVE] https://vk.com/gim225507433?sel={user_id}")


# Обработка лайка
@bot.on.raw_event(GroupEventType.LIKE_ADD)
async def like_add_handler(event):
    user_id = event['object']['liker_id']
    if event['object']['object_type'] != "post":
        return
    score = await data.change_score(user_id, 10000)
    score = "{:,}".format(score).replace(",", " ")
    try:
        await bot.api.messages.send(
            user_id=user_id,
            message=f"🎉 Вы получили {score} SG₽ за лайк!",
            random_id=random.randint(0, 2 ** 64)
        )
    except Exception as e:
        pass


# Обработка снятия лайка
@bot.on.raw_event(GroupEventType.LIKE_REMOVE)
async def like_remove_handler(event):
    user_id = event['object']['liker_id']
    if event['object']['object_type'] != "post":
        return
    await data.change_score(user_id, -10000)
    try:
        await bot.api.messages.send(
            user_id=user_id,
            message="😢 Вы потеряли 10 000 SG₽ за снятие лайка!",
            random_id=random.randint(0, 2 ** 64)
        )
    except Exception as e:
        pass

# Обработка VK Pay
@bot.on.message(CommandRule(["/vkpay"]))
async def vkpay_message(message: Message):
    _kb = keyboard.get_pay_keyboard()
    await message.answer("🎉 Поддержать проект можно через VK Pay", keyboard=_kb)

old_payment_time = {}
@bot.on.raw_event(GroupEventType.VKPAY_TRANSACTION)
async def vkpay_transaction_handler(event):
    if event['object']['date'] == old_payment_time.get(event['object']['from_id'], 0):
        return
    old_payment_time[event['object']['from_id']] = event['object']['date']
    user_id = event['object']['from_id']
    amount = event['object']['amount'] / 2
    score = await data.change_score(user_id, amount)
    try:
        await bot.api.messages.send(
            user_id=user_id,
            message=f"🎉 Вы получили {score*2} SG₽!",
            random_id=random.randint(0, 2 ** 64)
        )
    except Exception as e:
        raise e
    
@bot.on.raw_event([GroupEventType.DONUT_SUBSCRIPTION_CREATE, GroupEventType.DONUT_SUBSCRIPTION_EXPIRED, GroupEventType.DONUT_SUBSCRIPTION_CANCELLED])
async def donut_subscription_handler(event):
    await data.update_donuts()

@bot.on.message(WalletRule())
async def wallet_message(message: Message):
    await data.set_wallet(message.from_id, message.text)
    await message.answer("📦 Кошелек успешно установлен!")
    logging.info(f"[WALLET] {message.from_id} set wallet {message.text}")


@bot.on.message(text='/save')
async def save_message(message: Message):
    if message.from_id != 434356505:
        return
    await data.save_scores()
    await data.save_last_mines()
    await data.save_top()
    await message.answer("📦 Данные сохранены!")

@bot.on.message(text='/donut')
async def donut_message(message: Message):
    if message.from_id != 434356505:
        return
    await data.update_donuts()
    await message.answer("🎉 Донатеры обновлены!")

@bot.on.message(text='/top')
async def top_refresh_message(message: Message):
    if message.from_id != 434356505:
        return
    await data.check_top()
    await message.answer("🎉 Топ обновлён!")

@bot.on.message(CommandRule(["/bonus"]))
async def bonus_message(message: Message):
    if message.from_id != 434356505:
        return
    target_id = int(message.text.split()[1])
    bonus = int(message.text.split()[2])
    score = await data.change_score(target_id, bonus)
    await message.answer(f"🎉 Выдано {score} SG₽ пользователю {target_id}")
    await bot.api.messages.send(
        user_id=target_id,
        message=f"🎉 Вы получили бонус в размере {bonus} SG₽!",
        random_id=random.randint(0, 2 ** 64)
    )

@bot.on.message(CommandRule(["/sleep"]))
async def sleep_message(message: Message):
    if message.from_id != 434356505:
        return
    sleep_time = int(message.text.split()[1])
    data.set_sleep_time(sleep_time)
    await message.answer(f"💤 Установлено время сна {sleep_time} сек")

@bot.on.message(CommandRule(["/widget"]))
async def widget_message(message: Message):
    if message.from_id != 434356505:
        return
    await widget.update()
    await message.answer("🎨 Виджет обновлён!")


@bot.loop_wrapper.interval(minutes=5)
async def save_scores():
    try:
        await data.save_scores()
        await data.save_last_mines()
        await data.save_top()
        await data.update_donuts()
        await widget.update()
        response = await bot.api.request("groups.getOnlineStatus", {"group_id": 225507433})
        if response['response']["status"] != "online":
            await bot.api.groups.enable_online(group_id=225507433)
    except Exception as e:
        print(f"Error saving scores: {e}")
        await bot.api.messages.send(
            user_id=434356505,
            message=f"Error saving scores: {e}\n\n{traceback.format_exc()}",
            random_id=random.randint(0, 2 ** 64)
        )

bot.run_forever()