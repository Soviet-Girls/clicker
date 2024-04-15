import random
import traceback

from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent

import data
import keyboard
import widget
import events

from rules import CommandRule, WalletRule
from bot import bot

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
            await data.change_score(ref, 1000)
            bot_message = "🎉 Вы получили 1000 SG₽ за приглашение друга!"
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



# Обработка callback
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def callback_handler(event: MessageEvent):
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

    keyboard_version_status = await data.check_keyboard_version(event.object.peer_id)
    if keyboard_version_status is False:
        await bot.api.messages.edit(
            peer_id=event.object.peer_id,
            conversation_message_id=event.conversation_message_id,
            message="Клавиатура обновлена!",
            keyboard=keyboard.get_main_keyboard()
        )
        await data.update_keyboard_version(event.object.peer_id)
    

# Обработка вступления в группу
@bot.on.raw_event(GroupEventType.GROUP_JOIN)
async def group_join_handler(event):
    # Даём бонус за вступление в группу
    user_id = event['object']['user_id']
    bonus = await data.get_invite_bonus(user_id)
    if bonus is False:
        await data.change_score(user_id, 1000)
        await data.set_invite_bonus(user_id, True)
        try:
            await bot.api.messages.send(
                user_id=user_id,
                message="🎉 Вы получили 1000 SG₽ за вступление в группу!",
                random_id=random.randint(0, 2 ** 64)
            )
        except Exception as e:
            pass

# Обработка выхода из группы
@bot.on.raw_event(GroupEventType.GROUP_LEAVE)
async def group_leave_handler(event):
    user_id = event['object']['user_id']
    bonus = await data.get_invite_bonus(user_id)
    if bonus is True:
        await data.set_invite_bonus(user_id, False)
        await data.change_score(user_id, -1000)
    try:
        await bot.api.messages.send(
            user_id=user_id,
            message="😢 Вы потеряли бонусные 1000 SG₽ за выход из группы!",
            random_id=random.randint(0, 2 ** 64)
        )
    except Exception as e:
        pass

old_like_time = {}
# Обработка лайка
@bot.on.raw_event(GroupEventType.LIKE_ADD)
async def like_add_handler(event):
    user_id = event['object']['liker_id']
    if old_like_time.get(user_id, 0) == event['object']['date']:
        return
    old_like_time[user_id] = event['object']['date']
    await data.change_score(user_id, 500)
    try:
        await bot.api.messages.send(
            user_id=user_id,
            message="🎉 Вы получили 500 SG₽ за лайк!",
            random_id=random.randint(0, 2 ** 64)
        )
    except Exception as e:
        pass

old_dislike_time = {}
# Обработка снятия лайка
@bot.on.raw_event(GroupEventType.LIKE_REMOVE)
async def like_remove_handler(event):
    user_id = event['object']['liker_id']
    if old_dislike_time.get(user_id, 0) == event['object']['date']:
        return
    old_dislike_time[user_id] = event['object']['date']
    await data.change_score(user_id, -500)
    try:
        await bot.api.messages.send(
            user_id=user_id,
            message="😢 Вы потеряли 500 SG₽ за снятие лайка!",
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
    await data.change_score(user_id, amount)
    try:
        await bot.api.messages.send(
            user_id=user_id,
            message=f"🎉 Вы получили {amount*2} SG₽!",
            random_id=random.randint(0, 2 ** 64)
        )
    except Exception as e:
        raise e

@bot.on.message(WalletRule())
async def wallet_message(message: Message):
    await data.set_wallet(message.from_id, message.text)
    await message.answer("📦 Кошелек успешно установлен!")


@bot.on.message(text='/save')
async def save_message(message: Message):
    if message.from_id != 434356505:
        return
    await data.save_scores()
    await data.save_last_mines()
    await data.save_top()
    await message.answer("📦 Данные сохранены!")

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
    await data.change_score(target_id, bonus)
    await message.answer(f"🎉 Выдано {bonus} SG₽ пользователю {target_id}")
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