import asyncio
import time
from bot import bot

ver = "0"
sleep_time = 0

scores = {}
async def save_scores() -> None:
    for user_id, score in scores.items():
        _i = 0
        while True:
            try:
                await bot.api.storage.set("score"+ver, value=str(score), user_id=user_id)
                print(f"Score for user {user_id} saved: {score}")
                break
            except Exception as e:
                print(f"Error saving score for user {user_id}: {e}")
                asyncio.sleep(1)
                _i += 1
                if _i > 5:
                    break

last_mines = {}
async def save_last_mines() -> None:
    for user_id, last_mine in last_mines.items():
        _i = 0
        while True:
            try:
                await bot.api.storage.set("last_mine"+ver, value=str(last_mine), user_id=user_id)
                print(f"Last mine for user {user_id} saved: {last_mine}")
                break
            except Exception as e:
                print(f"Error saving last mine for user {user_id}: {e}")
                asyncio.sleep(1)
                _i += 1
                if _i > 5:
                    break


# donut

donuts = []

async def update_donuts() -> None:
    global donuts
    donuts = await bot.api.groups.get_members(group_id=225507433, filter="donut")
    donuts = [donut for donut in donuts.items]
    print(donuts)

async def is_donut(user_id: int) -> bool:
    if donuts == []:
        await update_donuts()
    return user_id in donuts


# топ 5 игроков (пары [user_id, score])
top = []

async def check_top() -> None:
    global top
    scores_data = {k: int(v) for k, v in scores.items() if not isinstance(v, str)}
    top = sorted(scores_data.items(), key=lambda x: x[1], reverse=True)[:5]
    if len(top) < 5:
        _top = await bot.api.storage.get("top"+ver, user_id=1)
        if _top != "":
            top = eval(_top[0].value)

last_check_top = 0
async def get_top() -> list:
    global last_check_top
    if time.time() - last_check_top > 60:
        await check_top()
        last_check_top = time.time()
    return top

async def save_top() -> None:
    await check_top()
    _i = 0
    while True:
        try:
            await bot.api.storage.set("top"+ver, user_id=1, value=str(top))
            print("Top saved")
            break
        except Exception as e:
            print(f"Error saving top: {e}")
            asyncio.sleep(1)
            _i += 1
            if _i > 5:
                break

pricing = [
    [15, 2],
    [100, 5],
    [1000, 10],
    [3000, 20],
    [10000, 50],
    [40000, 100],
    [500000, 200]
]

def price_count(level: int) -> int:
    if len(pricing) > level:
        return pricing[level]
    else:
        # и так до бесконечности
        price = pricing[-1][0] * 1.5
        income = pricing[-1][1] * 1.1
        for _ in range(level - len(pricing) + 1):
            price *= 1.5
            income *= 1.1
        return [int(price), int(income)]
    
# refs

refs = {}

async def get_ref(user_id: int) -> int:
    ref = refs.get(user_id, -1)
    if ref == -1:
        ref = await bot.api.storage.get("ref"+ver, user_id=user_id)
        ref = ref[0].value
        refs[user_id] = ref
    return 0 if ref == "" else int(ref)

async def set_ref(user_id: int, ref: int) -> None:
    await bot.api.storage.set("ref"+ver, value=str(ref), user_id=user_id)
    refs[user_id] = ref

# ref count

refs_count = {}

async def get_ref_count(user_id: int) -> int:
    ref_count = refs_count.get(user_id, -1)
    if ref_count == -1:
        ref_count = await bot.api.storage.get("ref_count"+ver, user_id=user_id)
        ref_count = ref_count[0].value
        refs_count[user_id] = ref_count
    return 0 if ref_count == "" else int(ref_count)

async def change_ref_count(user_id: int, count: int) -> None:
    ref_count = await get_ref_count(user_id)
    ref_count += count
    await bot.api.storage.set("ref_count"+ver, value=str(ref_count), user_id=user_id)
    refs_count[user_id] = ref_count

async def get_all_ref_count() -> list:
    users = await bot.api.messages.get_conversations()
    users = users.items
    ref_counts = []
    for user in users:
        _id = user.conversation.peer.id
        ref_count = await get_ref_count(_id)
        ref_counts.append([_id, ref_count])
    return ref_counts

async def get_ref_count_top() -> list:
    ref_counts = await get_all_ref_count()
    ref_counts = sorted(ref_counts, key=lambda x: x[1], reverse=True)[:5]
    return ref_counts

# score

async def get_score(user_id: int) -> int:
    score = scores.get(user_id, -1)
    if score == -1:
        score = await bot.api.storage.get("score"+ver, user_id=user_id)
        score = score[0].value
        scores[user_id] = score
    return 0 if score == "" else int(score)


async def change_score(user_id: int, points: int) -> None:
    ref = await get_ref(user_id)
    donut = await is_donut(user_id)
    if points > 0 and donut:
        points *= 2
    if ref != 0:
        if points > 99:
            ref_score = await get_score(ref)
            ref_score += points // 100
        else:
            ref_score = await get_score(ref)
            ref_score += 1
        scores[ref] = ref_score
    score = await get_score(user_id)
    score += points
    scores[user_id] = score


# coins per click

levels = {}

async def get_level(user_id: int) -> int:
    level = levels.get(user_id, -1)
    if level == -1:
        level = await bot.api.storage.get("level"+ver, user_id=user_id)
        level = level[0].value
        levels[user_id] = level
    return 0 if level == "" else int(level)

async def upgrade_level(user_id: int) -> None:
    level = await get_level(user_id)
    new_level = level + 1
    await bot.api.storage.set("level"+ver, value=str(new_level), user_id=user_id)
    levels[user_id] = new_level


cpcs = {}

async def get_cpc(user_id: int) -> int:
    cpc = cpcs.get(user_id, -1)
    if cpc == -1:
        cpc = await bot.api.storage.get("cpc"+ver, user_id=user_id)
        cpc = cpc[0].value
        cpcs[user_id] = cpc
    return 1 if cpc == "" else int(cpc)

async def change_cpc(user_id: int, cpc: int) -> None:
    await bot.api.storage.set("cpc"+ver, value=str(cpc), user_id=user_id)
    cpcs[user_id] = cpc

async def upgrade_cpc(user_id: int) -> None:
    cpc = await get_cpc(user_id)
    await bot.api.storage.set("cpc"+ver, value=str(cpc*2), user_id=user_id)
    cpcs[user_id] = cpc*2

async def get_cpc_upgrade_price(user_id: int) -> int:
    cpc = await get_cpc(user_id)
    cpc_upgrade_price = int(cpc * 100)
    return cpc_upgrade_price

# automine status

automines = {}

async def get_automine_status(user_id: int) -> bool:
    automine = automines.get(user_id, None)
    if automine is None:
        automine = await bot.api.storage.get("automine"+ver, user_id=user_id)
        automine = False if automine[0].value == "" else bool(automine[0].value)
        automines[user_id] = automine
    return automine

async def automine_on(user_id: int) -> None:
    await bot.api.storage.set("automine"+ver, value="True", user_id=user_id)
    automines[user_id] = True

async def get_last_mine(user_id: int) -> int:
    last_mine = last_mines.get(user_id, -1)
    if last_mine == -1:
        last_mine = await bot.api.storage.get("last_mine"+ver, user_id=user_id)
        last_mine = last_mine[0].value
        last_mines[user_id] = last_mine
    return 0 if last_mine == "" else int(last_mine)

async def set_last_mine(user_id: int, time: int) -> None:
    last_mines[user_id] = time

# wallet

wallets = {}

async def get_wallet(user_id: int) -> str:
    wallet = wallets.get(user_id, None)
    if wallet is None:
        wallet = await bot.api.storage.get("wallet"+ver, user_id=user_id)
        wallet = wallet[0].value
        wallets[user_id] = wallet
    return wallet

async def set_wallet(user_id: int, wallet: str) -> None:
    await bot.api.storage.set("wallet"+ver, value=wallet, user_id=user_id)
    wallets[user_id] = wallet


# invite bonus

async def get_invite_bonus(user_id: int) -> int:
    invite_bonus = await bot.api.storage.get("invite_bonus"+ver, user_id=user_id)
    invite_bonus = invite_bonus[0].value
    return invite_bonus == "True"

async def set_invite_bonus(user_id: int, invite_bonus: bool) -> None:
    await bot.api.storage.set("invite_bonus"+ver, value=str(invite_bonus), user_id=user_id)


# sleep time

def get_sleep_time() -> int:
    return sleep_time

def set_sleep_time(new_sleep_time: int):
    global sleep_time
    sleep_time = new_sleep_time

# secret codes

secret_codes = {}

def get_secret_code(user_id: int) -> int:
    secret_code = secret_codes.get(user_id, 0)
    return secret_code

def set_secret_code(user_id: int, secret_code: int) -> None:
    secret_codes[user_id] = secret_code

# keyboard update

actual = 4
async def get_keyboard_version(user_id: int) -> str:
    keyboard = await bot.api.storage.get("keyboard"+ver, user_id=user_id)
    keyboard = keyboard[0].value
    return 0 if keyboard == "" else int(keyboard)

async def update_keyboard_version(user_id: int) -> None:
    await bot.api.storage.set("keyboard"+ver, value=str(actual), user_id=user_id)

async def check_keyboard_version(user_id: int) -> bool:
    current = await get_keyboard_version(user_id)
    return current == actual


# quests

async def get_quests(user_id: int) -> list:
    quests = await bot.api.storage.get("quests"+ver, user_id=user_id)
    quests = quests[0].value
    return [] if quests == "" else eval(quests)

async def set_quests(user_id: int, quests: list) -> None:
    await bot.api.storage.set("quests"+ver, value=str(quests), user_id=user_id)

async def add_quest(user_id: int, quest: int) -> None:
    quests = await get_quests(user_id)
    quests.append(quest)
    await bot.api.storage.set("quests"+ver, value=str(quests), user_id=user_id)