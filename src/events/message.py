from random import choice

import discord
import discord.ext.commands

from config.values import (BOT_ID, CHANNEL_ID_INSCRIPTION, COLOR_ORANGE, COLOR_RED, EMOJI_ID_COLLIER)
import discord.ext
from utils.bot import bot
from utils.game.players import join
from utils.logging import get_logger
from utils.punishments import timeout

logger = get_logger(__name__)


async def on_message_event(message) -> None:
    """Gestion des messages"""

    await bot.process_commands(
        message
    )  # Execute les commandes, même si le message a été envoyé en DM au robot
    if message.author.id != BOT_ID:
        if ':collierimmunite:' in message.content:
            logger.warning(
                f'Use of immunity collar in message by : {message.author} (id:{message.author.id}).'
            )
            if not message.content.startswith('/'):
                await message.delete()
            logger.info(
                'Sending a message reminding of the rules relating to the immunity collar.'
            )
            embed = discord.Embed(
                title=':robot: RAPPEL AUX JOUEURS :moyai:',
                description=f":no_entry: L'usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}> est interdit sur le serveur afin de ne pas embrouiller les joueurs à la recherche du collier d'immunité.",
                color=COLOR_RED,
            )
            await message.channel.send(embed=embed)
            await timeout(
                message.author,
                reason=f"Usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}>",
            )
        elif message.channel.id == CHANNEL_ID_INSCRIPTION:
            logger.info('New message in the join channel.')
            if not message.content.startswith('/'):
                await message.delete()  # Supprime le message s'il ne s'agit pas d'une commande (auquel cas le message a déjà été supprimé)
                await join(message)
        elif not message.guild:
            if not message.content.startswith('/'):
                embed = discord.Embed(
                    title=':robot: **Je ne comprend que les commandes !** :moyai:',
                    description='Je suis incapable de répondre à tout autre contenu...',
                    color=COLOR_ORANGE,
                )
                embed.set_image(
                    url=choice(
                        [
                            'https://media.giphy.com/media/l2JhJGdpV4Uc3mffy/giphy.gif',
                            'https://media1.tenor.com/m/1fLwP04D_IIAAAAC/shrek-donkey.gif',
                            'https://media1.tenor.com/m/m8euCQ_x3U8AAAAC/kaamelott-arthur.gif',
                            'https://media1.tenor.com/m/VAgfPZcM340AAAAd/bof-i-dont-mind.gif',
                            'https://media1.tenor.com/m/LjCBqxySvecAAAAd/huh-rabbit.gif',
                            'https://media1.tenor.com/m/13frun_noiAAAAAC/miss-j-j-alexander.gif',
                        ]
                    )
                )
                await message.author.send(embed=embed)
