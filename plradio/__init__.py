from __future__ import annotations

from redbot.core.utils import get_end_user_data_statement

from pylav.types import BotT
from pylavcogs_shared.utils.required_methods import pylav_auto_setup

__red_end_user_data_statement__ = get_end_user_data_statement(__file__)

from plradio.cog import PyLavRadio


async def setup(bot: BotT):
    await pylav_auto_setup(bot, PyLavRadio)
