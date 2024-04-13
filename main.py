import time
import asyncio
import random
import traceback

from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent

import data
import keyboard
import widget

from rules import CommandRule, WalletRule
from bot import bot

refresh_message = {}

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

rocket_secret_codes = {}
    
async def generate_play_message(user_id: int, score: int = -1) -> str:
    if score == -1:
        score = await data.get_score(user_id)
    score = "{:,}".format(score).replace(",", " ")
    bot_message = f"💰 Твой счёт: {score} SG₽"
    sleep_time = data.get_sleep_time()
    if sleep_time == 0:
        bot_message += "\n\n⌛ Добыча доступна каждую секунду."
    else:
        bot_message += f"\n\n⌛ Высокая нагрузка! Добыча доступна каждые {sleep_time} секунд."
    wallet = await data.get_wallet(user_id)
    if wallet == "":
        bot_message += "\n\n⚠️ Кошелек Polygon не указан! Отправьте адрес кошелька боту, чтобы получить SG₽ после закрытия игры."
    else:
        wallet = wallet[:5] + "..." + wallet[-5:]
        bot_message += f"\n\n📦 Ваш кошелек: {wallet}.\n После закрытия игры SG₽ будут отправлены на этот адрес."

    rocket = random.randint(0, 20) == 0
    if rocket:
        rocket_secret_codes[user_id] = random.randint(1000, 9999)
    else:
        rocket_secret_codes[user_id] = 0
    kb = keyboard.get_play_keyboard(rocket, rocket_secret_codes[user_id])
    return bot_message, kb
    
# Обработка команды "🎮 Играть"
async def play_message(event: MessageEvent):
    bot_message, kb = await generate_play_message(event.object.peer_id)
    await bot.api.messages.send(
        user_id=event.object.peer_id,
        message=bot_message,
        keyboard=kb,
        random_id=random.randint(0, 2 ** 64)
    )
    await event.show_snackbar("🎮 Игра началась!")

# Обработка команды "🔝 Топ игроков"
async def top_message(event: MessageEvent):
    top = await data.get_top()
    bot_message = "🏆 Топ 5 игроков:\n\n"
    for i, user in enumerate(top):
        score = "{:,}".format(user[1]).replace(",", " ")
        user = await bot.api.users.get(user_ids=user[0])
        user = user[0]
        name = user.first_name + " " + user.last_name[0] + "."
        bot_message += f"{i+1}. {name} - {score} SG₽\n"
    await bot.api.messages.send(
        user_id=event.object.peer_id,
        message=bot_message,
        random_id=random.randint(0, 2 ** 64)
    )
    await event.show_snackbar("🔝 Топ игроков")

# Обработка команды "🛍️  Улучшения"
async def upgrades_message(event: MessageEvent):
    user_id = event.object.peer_id
    bot_message = "Выбери улучшение:"
    await bot.api.messages.send(
        user_id=user_id,
        message=bot_message,
        keyboard=await keyboard.get_upgrades_keyboard(user_id),
        random_id=random.randint(0, 2 ** 64)
    )
    await event.show_snackbar("🛍️ Улучшения")

# Обработка команды "🔼 Улучшение клика"
async def upgrade_cpc_message(event: MessageEvent):
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

# Обработка команды "🤖 Автодобыча"
async def upgrade_automine_message(event: MessageEvent):
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

# Обработка команды "🪙 ДОБЫТЬ!"
async def mine_message(event: MessageEvent):
    user_id = event.object.peer_id
    tm_last = await data.get_last_mine(user_id)
    tm = int(time.time())
    tm_diff = tm - tm_last
    sleep_time = data.get_sleep_time()
    _st = 1 if sleep_time == 0 else sleep_time
    if tm_diff < _st:
        egg = random.randint(0, 15)
        if egg == 0:
            await event.show_snackbar("⚡ Вы постите слишком быстро!")
        elif egg == 1:
            await event.show_snackbar("🛑 Куда гонишь, брат?")
        elif egg == 2:
            await event.show_snackbar("🛑 Притормози, родной")
        elif egg == 3:
            await event.show_snackbar("🌿 Сходи потрогай траву")
        else:
            await event.show_snackbar("🛑 Слишком быстро!")
        return
    cpc = await data.get_cpc(user_id)
    try:
        automine_status = await data.get_automine_status(user_id)
        if automine_status:
            if tm_diff > 600:
                new_cpc = int(tm_diff /2 * cpc / 100)
                if new_cpc > 10000:
                    new_cpc = 10000
                elif new_cpc < 1:
                    new_cpc = 1
                cpc += new_cpc
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
        await data.change_score(user_id, cpc)
        await data.set_last_mine(user_id, tm)
    except Exception as e:
        await event.show_snackbar("🛑 Слишком быстро!")
        raise e
    score = await data.get_score(user_id)
    _rm = refresh_message.get(user_id, 0)
    try:
        await event.show_snackbar(f"💸 {score} (+{cpc})")
    except Exception as e:
        print(f"Error showing snackbar: {e}")
        await asyncio.sleep(4)
        await event.show_snackbar(f"💸 {score} (+{cpc})")
    try:
        if _rm == 4:
            bot_message, kb = await generate_play_message(event.object.peer_id, score)
            await bot.api.messages.edit(
                peer_id=event.object.peer_id,
                conversation_message_id=event.conversation_message_id,
                message=bot_message,
                keyboard=kb,
                random_id=random.randint(0, 2 ** 64)
            )
            _rm = 0
        else:
            _rm += 1
        refresh_message[user_id] = _rm

    except Exception as e:
        print(f"Error editing message: {e}")


# Обработка команды "👥 Пригласить"
async def ref_message(event: MessageEvent):
    user_id = event.object.peer_id
    count = await data.get_ref_count(user_id)
    link = f"https://vk.me/soviet_clicker?ref={user_id}"
    bot_message = "👥 Отправь пригласительную ссылку друзьям, чтобы получить бонус 1000 SG₽ за каждого друга!\n\n"
    bot_message += "Также ты будешь поулчать бонусный 1% от добычи твоих друзей (он не будет отниматься у друзей).\n\n"
    bot_message += f"🧮 Приглашено друзей: {count}\n\n"
    bot_message += f"🔗 {link}"
    await bot.api.messages.send(
        user_id=user_id,
        message=bot_message,
        random_id=random.randint(0, 2 ** 64)
    )


# Обработка команды "🚀 БОНУС!"
async def rocket_message(event: MessageEvent):
    user_id = event.object.peer_id
    secret_code = rocket_secret_codes.get(user_id, 0)
    if secret_code == 0:
        await event.show_snackbar("🥲 Код бонуса просрочен")
        return
    elif event.object.payload.get("command") != f"rocket-{secret_code}":
        await event.show_snackbar("🤡 Хорошая попытка")
        return
    else:
        rocket_secret_codes[user_id] = 0
    score = await data.get_score(user_id)
    cpc = await data.get_cpc(user_id)
    bonus = cpc * 5
    try:
        await data.change_score(user_id, bonus)
        await event.show_snackbar(f"🚀 {score} (+{bonus})")
        bot_message, kb = await generate_play_message(user_id)
        await bot.api.messages.edit(
            peer_id=user_id,
            conversation_message_id=event.conversation_message_id,
            message=bot_message,
            keyboard=kb,
            random_id=random.randint(0, 2 ** 64)
        )
    except Exception as e:
        await event.show_snackbar("🛑 Слишком быстро!")
        raise e
    
    
# Обработка callback
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def callback_handler(event: MessageEvent):
    if event.object.payload.get("command") == "play":
        await play_message(event)
    elif event.object.payload.get("command") == "mine":
        await mine_message(event)
    elif event.object.payload.get("command") == "upgrades":
        await upgrades_message(event)
    elif event.object.payload.get("command") == "upgrade_cpc":
        await upgrade_cpc_message(event)
    elif event.object.payload.get("command") == "upgrade_automine":
        await upgrade_automine_message(event)
    elif event.object.payload.get("command") == "ref":
        await ref_message(event)
    elif event.object.payload.get("command") == "top":
        await top_message(event)
    elif event.object.payload.get("command").startswith("rocket-"):
        await rocket_message(event)

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
        await bot.api.groups.enable_online(group_id=225507433)
    except Exception as e:
        print(f"Error saving scores: {e}")
        await bot.api.messages.send(
            user_id=434356505,
            message=f"Error saving scores: {e}\n\n{traceback.format_exc()}",
            random_id=random.randint(0, 2 ** 64)
        )

bot.run_forever()