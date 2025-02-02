__version__ = (1, 0, 0)
# scope: hikka_only
# scope: hikka_min 1.6.3

import logging

from telethon import types

from .. import loader, utils


logger = logging.getLogger(__name__)


@loader.tds
class Mod(loader.Module):
    """Test mod? Idk"""

    strings = {
        "name": "TestMod",
        "meow": "meow {ascii}"
    }


    @loader.command()
    async def meowcmd(self, message: types.Message):
        """Get meow"""
        
        await utils.answer(
            message,
            self.strings("meow").format(
                ascii=utils.ascii_face()
            )
        )