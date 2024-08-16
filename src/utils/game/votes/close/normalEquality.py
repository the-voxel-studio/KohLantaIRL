import datetime

import discord

from config.values import CHANNEL_ID_RESULTATS, COLOR_ORANGE, GUILD_ID
from database.game import Game
from database.votelog import VoteLog, get_council_number
from utils.bot import bot
from utils.log import get_logger

from .. import eliminate

logger = get_logger(__name__)

select_options = []


class EqualityView(discord.ui.View):
    """Equality view for the vote after an equality."""

    def __init__(self):
        """Initialize the view."""

        super().__init__(timeout=None)
        self.council_number = get_council_number()
        self.select = discord.ui.Select(
            placeholder='Choisis une personne à éliminer !',
            min_values=1,
            max_values=1,
            options=select_options,
            custom_id='tied_players_selection',
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)
        logger.info(f'EqualityView __init__ > OK | select_options: {select_options}')

    async def select_callback(self, interaction):
        """Callback for the select."""

        logger.info(f'EqualityView select_callback > start | user: {interaction.user} (id: {interaction.user.id})')
        await interaction.response.defer()
        self.select.disabled = True
        await interaction.message.edit(view=self)
        now_date = datetime.datetime.now()
        last_vote_date = datetime.datetime.strptime(
            VoteLog(last=True).object.date, '%d/%m/%Y %H:%M:%S'
        )
        time_delta = now_date - last_vote_date
        in_time = time_delta < datetime.timedelta(hours=17)  # 14h the day after the tie vote
        if in_time:
            eliminated_nickname = interaction.data['values'][0]
            embed = discord.Embed(
                title=f'**Tu as éliminé {eliminated_nickname} !**', color=9807270
            )
            embed.set_author(
                name=f'Egalité au conseil n°{self.council_number} !',
                icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
            )
            embed.set_thumbnail(
                url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
            )
            guild = bot.get_guild(GUILD_ID)
            member = discord.utils.get(guild.members, nick=eliminated_nickname)
            await eliminate(interaction, member, 'After equality')
            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title=':robot: Trop tard ! :moyai:',
                description=':no_entry: Le selection est maintenant fermée, vous avez dépacé le délais imparti. Par votre faute, les deux joueurs ont dors et déjà été éliminés !',
                color=COLOR_ORANGE,
            )
            embed.set_footer(
                text="Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur."
            )
            embed.set_image(url='https://media.tenor.com/CCLg0rGFVHEAAAAC/ah-denis.gif')
            await interaction.followup.send(embed=embed)
        logger.info(f'EqualityView select_callback > OK | user: {interaction.user} (id: {interaction.user.id}) | in_time: {in_time}')


async def close_normal_equality(
    reactions_list, cheaters_number, council_number, it_is_the_final, tied_players
) -> None:
    """Close the normal vote after an equality."""

    global select_options
    logger.info('close_normal_equality > start ')
    VoteLog(data={
        'votes': reactions_list,
        'cheaters_number': cheaters_number,
        'tied_players': tied_players,
    }).save()
    embed = discord.Embed(
        title='**Egalité**',
        description="Les aventuriers de la tribu n'ont pas sus se décider !",
        color=9807270,
    )
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    if it_is_the_final:
        vote_denomination = 'final'
        vote_chooser1 = 'Le vainqueur de la saison précédente'
        vote_chooser2 = 'dernier vainqueur en date'
        vote_chooser_id = Game.last_winner_id
    else:
        vote_denomination = f'n°{council_number}'
        vote_chooser1 = 'La dernière personne éliminée'
        vote_chooser2 = 'dernière personne éliminée'
        try:
            vote_chooser_id = VoteLog(last=-1).object.eliminated[0].id
        except IndexError:
            vote_chooser_id = VoteLog(last=-2).object.eliminated[0].id

    embed.set_author(
        name=f'Résultat du conseil {vote_denomination}',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.add_field(
        name=f'{vote_chooser1} doit maintenant trancher entre les personnes étant actuellement à égalité.',
        value='Vous serez avertis via ce canal dès la décision prise et saisie.',
        inline=True,
    )
    channel = bot.get_channel(CHANNEL_ID_RESULTATS)
    await channel.send(embed=embed)
    max_date = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(
        hour=12, minute=0, second=0, microsecond=0
    )
    embed = discord.Embed(
        title='**A toi de choisir !**',
        description=f"En tant que {vote_chooser2}, tu dois décider de l'issue de ce vote {vote_denomination} !\nTu dois choisir ci-dessous entre les personnes arrivées à égalité.\nAttention, toute sélection est définitive.\nTu dois faire ton choix avant la date suivante : {max_date.strftime('%d/%m/%Y %H:%M:%S')}",
        color=9807270,
    )
    embed.set_author(
        name=f'Egalité au conseil {vote_denomination} !',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    chooser = discord.utils.get(bot.get_all_members(), id=vote_chooser_id)
    select_options = [
        discord.SelectOption(label=p.nickname, description=f'Eliminer {p.nickname}')
        for p in tied_players
    ]
    await chooser.send(embed=embed, view=EqualityView())
    logger.info('close_normal_equality > OK ')
