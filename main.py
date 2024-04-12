import time
import asyncio
import random

from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent

import data
import keyboard

from rules import CommandRule, WalletRule
from bot import bot

refresh_message = {}

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
    
async def generate_play_message(user_id: int) -> str:
    score = await data.get_score(user_id)
    score = "{:,}".format(score).replace(",", " ")
    bot_message = f"💰 Твой счёт: {score} SG₽"
    bot_message += "\n\n⌛ Добыча доступна каждую секунду."
    wallet = await data.get_wallet(user_id)
    if wallet == "":
        bot_message += "\n\n⚠️ Кошелек Polygon не указан! Отправьте адрес кошелька боту, чтобы получить SG₽ после закрытия игры."
    else:
        wallet = wallet[:5] + "..." + wallet[-5:]
        bot_message += f"\n\n📦 Ваш кошелек: {wallet}.\n После закрытия игры SG₽ будут отправлены на этот адрес."
    return bot_message
    
# Обработка команды "🎮 Играть"
async def play_message(event: MessageEvent):
    bot_message = await generate_play_message(event.object.peer_id)
    await bot.api.messages.send(
        user_id=event.object.peer_id,
        message=bot_message,
        keyboard=keyboard.get_play_keyboard(),
        random_id=random.randint(0, 2 ** 64)
    )
    await event.show_snackbar("🎮 Игра началась!")

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
    cpc = await data.get_cpc(user_id)
    try:
        tm = int(time.time())
        automine_status = await data.get_automine_status(user_id)
        if automine_status:
            tm_last = await data.get_last_mine(user_id)
            tm_diff = tm - tm_last
            new_cpc = int(tm_diff /2 * cpc / 100)
            if new_cpc > 10000:
                new_cpc = 10000
            elif new_cpc < 1:
                new_cpc = 1
            cpc += new_cpc
        # await asyncio.sleep(6)
        await data.change_score(user_id, cpc)
        await data.set_last_mine(user_id, tm)
    except Exception as e:
        await event.show_snackbar("🛑 Слишком быстро!")
        raise e
    score = await data.get_score(user_id)
    _rm = refresh_message.get(user_id, 0)
    try:
        await event.show_snackbar(f"🪙 {score} (+{cpc})")
    except Exception as e:
        print(f"Error showing snackbar: {e}")
        await asyncio.sleep(4)
        await event.show_snackbar(f"🪙 {score} (+{cpc})")
    try:
        if _rm == 4:
            bot_message = await generate_play_message(event.object.peer_id)
            await bot.api.messages.edit(
                peer_id=event.object.peer_id,
                conversation_message_id=event.conversation_message_id,
                message=bot_message,
                keyboard=keyboard.get_play_keyboard(),
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
    await message.answer("📦 Данные сохранены!")

@bot.on.message(CommandRule(["/bonus"]))
async def bonus_message(message: Message):
    target_id = int(message.text.split()[1])
    bonus = int(message.text.split()[2])
    await data.change_score(target_id, bonus)
    await message.answer(f"🎉 Выдано {bonus} SG₽ пользователю {target_id}")


@bot.loop_wrapper.interval(minutes=5)
async def save_scores():
    await data.save_scores()
    await data.save_last_mines()

bot.run_forever()