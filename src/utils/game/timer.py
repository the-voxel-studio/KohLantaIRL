import asyncio
import datetime
from os import system
from threading import Timer
import random
import utils.game.votes as vote
from database.game import Game
from database.votelog import get_council_number
from utils.bot import bot
from utils.log import send_log
from utils.logging import get_logger
from utils.game.immuniteCollar import send_immunite_collar
logger = get_logger(__name__)
timer_thread = None


async def timed_action():
    """Timer loop for the game."""

    logger.info('fn > Timer Loop > A thread timer has ended.')
    time = datetime.datetime.now()
    hour = int(time.strftime('%H'))

    if hour == 10 * random() + 10 * random() and get_council_number() >= 4 and Game.immunite_collar_msg_id == 0 and Game.immunite_collar_player_id == 0:
        send_immunite_collar()

    if hour == 1:
        logger.warning('Preparing for automatic reboot.')
        timer_thread.cancel()
        await send_log('Redémarrage automatique en cours', color='orange')
        logger.info('Ready to reboot.')
        system('sudo reboot')
    elif hour == 14 and Game.state == 1:
        await vote.check_if_last_eliminate_is_saved()
    elif hour == 17 and Game.state in [1, 2]:
        await vote.open()
    elif hour == 21 and Game.vote_msg_id != 0 and Game.state == 1:
        await vote.close()
    elif hour == 0 and Game.vote_msg_id != 0 and Game.state == 3:
        Game.game_end()
        await vote.close()
    await start_new_timer()


def timed_action_sync():
    """Run the timed_action function in the bot loop."""

    coro = timed_action()
    asyncio.run_coroutine_threadsafe(coro, bot.loop)


async def start_new_timer():
    """Start a new timer thread."""

    global timer_thread
    time = datetime.datetime.today()
    next_time = time.replace(
        day=time.day, hour=time.hour, minute=0, second=0, microsecond=0
    ) + datetime.timedelta(hours=1)
    delta = (next_time - time).total_seconds()
    if delta == 0:
        logger.info(
            f'fn > Timer Loop > Waiting for {time.hour+1}:00:00 to start a new thread timer'
        )
        while delta == 0:
            next_time = time.replace(
                day=time.day, hour=time.hour, minute=0, second=0, microsecond=0
            ) + datetime.timedelta(hours=1)
            delta = (next_time - time).total_seconds()
    timer_thread = Timer(delta, timed_action_sync)
    timer_thread.start()
    logger.info(f'fn > Timer Loop > New thread timer triggered | delta: {delta}')


def cancel_timer():
    """Cancel the timer thread."""

    try:
        timer_thread.cancel()
        logger.info('One timer canceled.')
    except AttributeError:
        logger.info('Any timer to cancel.')
