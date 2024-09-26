import datetime

import discord
import discord.ext.commands

from cogs.how_to import AllianceView
from config.values import MODE
import discord.ext

from utils.bot import bot
from utils.game.alliances import purge_empty_alliances
from utils.game.immunity.collar import move_immunite_collar_down
from utils.game.timer import start_new_timer
from utils.game.votes.close.normalEquality import EqualityView
from utils.log import send_log, send_logs_file
from utils.logging import get_logger

logger = get_logger(__name__)


async def on_ready_event(COGS: list[str]) -> None:
    """Lancement du robot"""

    for cog in COGS:
        try:
            await bot.load_extension(cog)
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            logger.warning(f'Extension {cog} already loaded.')
    time = datetime.datetime.now().strftime('%d/%m/%Y **%H:%M**')
    deleted_count = await purge_empty_alliances()
    await start_new_timer()
    await send_logs_file()
    bot.add_view(EqualityView())
    bot.add_view(AllianceView())
    await move_immunite_collar_down()
    synced = await bot.tree.sync()
    bot_mode = MODE.upper() if MODE else 'PRODUCTION'
    color = 'green' if bot_mode == 'PRODUCTION' else 'orange'
    await send_log(
        'BOT restarted and ready',
        f':tools: mode : **{bot_mode}**',
        f':clock: time : {time}',
        f':handshake: empty alliances deleted : **{deleted_count}**',
        f':dividers: cogs loaded : **{len(COGS)}**',
        f':control_knobs: app commands : **{len(synced)}**',
        color=color,
    )
    logger.info('Bot started and ready.')
