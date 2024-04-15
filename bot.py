import config
from vkbottle.bot import Bot
from vkbottle import API

bot = Bot(config.VK_TOKEN)
user_api = API(config.VK_ADMIN)