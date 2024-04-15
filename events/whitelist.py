import random
from vkbottle.bot import MessageEvent

import data
from bot import bot

def save_wallet(wallet, status):
    if status == 1:
        try:
            with open("wallets_regular.txt", "r") as f:
                wallets = f.read().split("\n")
            if wallet in wallets:
                return False
        except FileNotFoundError:
            pass
        with open("wallets_regular.txt", "a") as f:
            f.write(wallet + "\n")
    elif status == 0:
        try:
            with open("wallets_top5.txt", "r") as f:
                wallets = f.read().split("\n")
            if wallet in wallets:
                return False
        except FileNotFoundError:
            pass
        with open("wallets_top5.txt", "a") as f:
            f.write(wallet + "\n")
    return True

# Обработка команды "🖼️ Получить NFT"
async def message(event: MessageEvent):
    await event.show_snackbar("🖼️ Получить NFT")
    user_id = event.object.peer_id
    top = await data.get_top()
    wallet = await data.get_wallet(user_id)
    if wallet == "":
        bot_message = "⚠️ Кошелек Polygon не указан! Отправьте адрес кошелька боту, чтобы получить SG₽ после закрытия игры."
        await bot.api.messages.send(
            user_id=user_id,
            message=bot_message,
            random_id=random.randint(0, 2 ** 64)
        )
        return
    
    score = await data.get_score(user_id)
    if score < 500:
        bot_message = "⚠️ У вас недостаточно SG₽ для получения NFT! Необходимо 500 SG₽."
        await bot.api.messages.send(
            user_id=user_id,
            message=bot_message,
            random_id=random.randint(0, 2 ** 64)
        )
        return
    in_top = False
    for i, user in enumerate(top):
        if user[0] == event.object.peer_id:
            check = save_wallet(wallet, 0)
            bot_message = "🎉 Поздравляем! Вы получите NFT со статусом <<Топовый игрок>>! Токен будет отправлен на ваш кошелек в течение недели."
            in_top = True
            break
    if not in_top:
        check = save_wallet(wallet, 1)
        bot_message = "🎉 Вы добавлены в вайтлист! Токен будет отправлен на ваш кошелек в течение недели."
    if check is False:
        bot_message = "⚠️ Вы уже в вайтлисте!"
    else:
        await data.change_score(user_id, -500)
    await bot.api.messages.send(
        user_id=event.object.peer_id,
        message=bot_message,
        random_id=random.randint(0, 2 ** 64)
    )