from typing import Tuple
from vkbottle import ABCRule
from vkbottle.bot import Message


class CommandRule(ABCRule):
    def __init__(self, commands: Tuple[str, ...]):
        self.commands = commands

    async def check(self, message: Message) -> bool:
        if message.text is None:
            return False
        elif message.text == '':
            return False
        return message.text.lower().split()[0] in self.commands
    

class WalletRule(ABCRule):
    async def check(self, message: Message) -> bool:
        if message.text.startswith('0x') and len(message.text) == 42:
            return True
        return False