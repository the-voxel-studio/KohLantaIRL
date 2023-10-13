import discord

from config.values import (CHANNEL_ID_GENERAL, COLOR_GREEN, COLOR_ORANGE,
                           USER_ID_ADMIN)
from utils.bot import bot
from utils.logging import get_logger
from utils.models import NewPlayer, Player, Variables

logger = get_logger(__name__)

async def join(message):
    """Inscription au jeu
    
    Cette fonctione permet de s'inscrire dans le jeu.
    Elle récupère le prenom et l'initiale fournie, crée l'arboréscence dans la base de donnée et attribue le role de "joueur"
    
    Parameters
    ----------
    message:
		Objet message envoyé dans le channel "inscription"
        Contient le contenu, l'auteur, le channel, la guild...
    """
    logger.info(f"fn > join > start | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")
    args = message.content.split(" ") # Découpe du texte du contenu en fonciton des espaces
    player = message.author # Récupère le joueur ayant envoyé la commande
    if Variables.get_state(): # Vérification du statut du jeu : les inscriptions ne doivent pas être closes
        logger.warning(f"fn > join > GameAlreadyStarted | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")
        embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: La partie a déjà débutée", color=COLOR_ORANGE)
        await player.send(embed=embed)
    elif Player(id=player.id).exists: # Recherche de l'identifiant unique Discord du joueur pour vérifier qu'il n'est pas déjà inscrit
        logger.warning(f"fn > join > PlayerAlreadyJoined | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")
        embed=discord.Embed(title=f":robot: Action inutile :moyai:", description=f":white_check_mark: Vous êtes déjà inscrit à cette partie.", color=COLOR_GREEN)
        embed.set_footer(text="En cas de problème, contacter un administrateur en MP.")
        await player.send(embed=embed)
    elif len(args) != 2 or len(args[0]) == 0 or len(args[1]) != 1: # Vérification du format des éléments fournis : deux éléments dont la longeur du premier doit être supérieure à 0 et du second doit être égale à 1
        logger.warning(f"fn > join > BadFormat | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")
        embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Vous devez renseigner votre prénom et initiale de nom comme suis : `Prénom N`\nDe plus, le prénom ne peut contenir d'espaces. Si besoin, utilisez des *-* .", color=COLOR_ORANGE)
        await player.send(embed=embed)
    else:
        nickname = "{} {}".format(args[0], args[1]) # Création d'une seule chaine de caractère sous le format "Arthur D"
        try:
            await player.edit(nick=nickname) # Tentative de renommage du joueur sur Discord sous le format ci-dessus
        except:
            logger.error(f"fn > join > PlayerEditError | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")
            embed=discord.Embed(title=f":robot: Faible erreur :moyai:", description=f":warning: Une erreur est survenue lors du changement de votre nom sur le serveur : Veuillez contacter <@{USER_ID_ADMIN}> pour qu'il effectue la modification manuellement.\nPas d'inquiétude, le processus d'inscription continue normalement, cela n'auras aucun impact.", color=COLOR_ORANGE) # En cas d'erreur (il s'agit d'une commande un peu capricieuse)
            await player.send(embed=embed)
        new_player = NewPlayer() # Création d'un nouvel objet "joueur" dans la base de donnée
        new_player.id = player.id
        new_player.nickname = nickname
        new_player.save() # Enregistrement du joueur dans la base de données
        role = discord.utils.get(message.guild.roles, name="Joueur") # Récupération du role "joueur"
        await player.add_roles(role) # Assignation du nouveau role
        embed=discord.Embed(title=f":robot: Bienvenue ! :moyai:", description=f":white_check_mark: Bienvenue dans cette saison de Koh Lanta IRL !\nTon compte a été paramétré avec succès, nous te laissons découvrir les différents salons et les différentes actions que tu peux effectuer sur ce serveur.\nA très vite !", color=COLOR_GREEN)
        await player.send(embed=embed)
        embed=discord.Embed(title=f":confetti_ball: On souhaite la bienvenue à **{nickname}** qui participera à la prochaine saison de Koh Lanta IRL !:confetti_ball:", color=COLOR_GREEN)
        await bot.get_channel(CHANNEL_ID_GENERAL).send(embed=embed)
        logger.info(f"fn > join > OK | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")