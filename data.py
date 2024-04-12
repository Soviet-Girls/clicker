import asyncio
from bot import bot

ver = "0"

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


# топ 5 игроков (пары [user_id, score])
top = []

async def check_top() -> None:
    global top
    scores_data = {k: int(v) for k, v in scores.items()}
    top = sorted(scores_data.items(), key=lambda x: x[1], reverse=True)[:5]
    if len(top) < 5:
        _top = await bot.api.storage.get("top"+ver, user_id=1)
        if _top != "":
            top = eval(_top[0].value)

async def get_top() -> list:
    if len(top) < 5:
        await check_top()
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

async def get_ref(user_id: int) -> int:
    ref = await bot.api.storage.get("ref"+ver, user_id=user_id)
    ref = ref[0].value
    return 0 if ref == "" else int(ref)

async def set_ref(user_id: int, ref: int) -> None:
    await bot.api.storage.set("ref"+ver, value=str(ref), user_id=user_id)

# ref count

async def get_ref_count(user_id: int) -> int:
    ref_count = await bot.api.storage.get("ref_count"+ver, user_id=user_id)
    ref_count = ref_count[0].value
    return 0 if ref_count == "" else int(ref_count)

async def change_ref_count(user_id: int, count: int) -> None:
    ref_count = await get_ref_count(user_id)
    ref_count += count
    await bot.api.storage.set("ref_count"+ver, value=str(ref_count), user_id=user_id)

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
    if ref != 0 and points > 99:
        ref_score = await get_score(ref)
        ref_score += points // 100
        scores[ref] = ref_score
    score = await get_score(user_id)
    score += points
    scores[user_id] = score


# coins per click

async def get_level(user_id: int) -> int:
    level = await bot.api.storage.get("level"+ver, user_id=user_id)
    level = level[0].value
    return 0 if level == "" else int(level)

async def upgrade_level(user_id: int) -> None:
    level = await get_level(user_id)
    new_level = level + 1
    await bot.api.storage.set("level"+ver, value=str(new_level), user_id=user_id)

async def get_cpc(user_id: int) -> int:
    cpc = await bot.api.storage.get("cpc"+ver, user_id=user_id)
    cpc = cpc[0].value
    return 1 if cpc == "" else int(cpc)

async def change_cpc(user_id: int, cpc: int) -> None:
    await bot.api.storage.set("cpc"+ver, value=str(cpc), user_id=user_id)

async def upgrade_cpc(user_id: int) -> None:
    cpc = await get_cpc(user_id)
    await bot.api.storage.set("cpc"+ver, value=str(cpc*2), user_id=user_id)

async def get_cpc_upgrade_price(user_id: int) -> int:
    cpc = await get_cpc(user_id)
    cpc_upgrade_price = int(cpc * 100)
    return cpc_upgrade_price

# automine status

async def get_automine_status(user_id: int) -> bool:
    automine = await bot.api.storage.get("automine"+ver, user_id=user_id)
    automine = automine[0].value
    return False if automine == "" else bool(automine)

async def automine_on(user_id: int) -> None:
    await bot.api.storage.set("automine"+ver, value="True", user_id=user_id)

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

async def get_wallet(user_id: int) -> str:
    wallet = await bot.api.storage.get("wallet"+ver, user_id=user_id)
    wallet = wallet[0].value
    return wallet

async def set_wallet(user_id: int, wallet: str) -> None:
    await bot.api.storage.set("wallet"+ver, value=wallet, user_id=user_id)


# invite bonus

async def get_invite_bonus(user_id: int) -> int:
    invite_bonus = await bot.api.storage.get("invite_bonus"+ver, user_id=user_id)
    invite_bonus = invite_bonus[0].value
    return invite_bonus == "True"

async def set_invite_bonus(user_id: int, invite_bonus: bool) -> None:
    await bot.api.storage.set("invite_bonus"+ver, value=str(invite_bonus), user_id=user_id)