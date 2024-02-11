import html
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (BaseDocTemplate, Frame, PageBreak,
                                PageTemplate, Paragraph, Table)

from utils.logging import get_logger
from utils.models import Player, VoteLog, get_alliances_number
import os

logger = get_logger(__name__)

logger.info(f"Setup running...")
DIRNAME = Path(__file__).parent.parent
DIRNAME = Path(__file__).parent.parent
styles = getSampleStyleSheet()
styles["Title"].textColor = colors.whitesmoke
styles["h2"].textColor = colors.whitesmoke
styles["h3"].textColor = colors.whitesmoke
styles["Normal"].textColor = colors.whitesmoke
styles["Normal"].bulletIndent = 25
styles["Normal"].leftIndent = 40

# [ ] add tied_players section

def background_canvas(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFillColor("#2b2d31")
    canvas_obj.rect(0, 0, A4[0], A4[1], fill=True, stroke=False)
    canvas_obj.restoreState()


def create_pdf(file_path, vote_number, **kwargs):
    logger.info(
        f"fn > create_pdf > start | file_path: {file_path} | vote_number: {vote_number}"
    )
    doc = BaseDocTemplate(
        file_path, pagesize=A4, leftMargin=50, title="KohLanta Saison 4 Vote 4 "
    )

    elements = []

    frame = Frame(0, 0, A4[0], A4[1], 50, 30, 50, 30, showBoundary=1)
    background_template = PageTemplate(
        id="background1", frames=[frame], onPage=background_canvas
    )
    doc.addPageTemplates([background_template])

    for el in render_vote(vote_number, last=True, **kwargs):
        elements.append(el)
    if vote_number > 1:
        for vote in range(vote_number - 1, 0, -1):
            for el in render_vote(vote):
                elements.append(el)

    for el in render_rules():
        elements.append(el)

    doc.build(elements)
    logger.info(
        f"fn > create_pdf > OK | file_path: {file_path} | vote_number: {vote_number}"
    )


def render_vote(number: int, **kwargs):
    logger.info(f"fn > render_vote > start | number: {number} | kwargs: {kwargs}")

    final = kwargs.get("final", False)

    vote_log = VoteLog(number=number)
    votes_number = len(vote_log.votes)

    players = Player(option="living").list

    votes = {v["voter"]: v["for"] for v in vote_log.votes}

    eliminated_players = Player(option="eliminated").list
    eliminated_players_number = len(eliminated_players)

    eliminated_at_this_vote = vote_log.eliminated
    eliminated_at_this_vote_number = len(eliminated_at_this_vote)

    if not final:

        in_vote_living_participants = [el for el in eliminated_players if el.get("deathCouncilNumber", 1000) >= number]

        players.extend(in_vote_living_participants)

    players_number = len(players)
    players__id = [p.get("_id") for p in players]
    players_username = [p.get("nickname") for p in players]

    last = kwargs.get("last", False)
    elements = []

    title = f"KohLanta Discord Saison 4<br />Vote n°{str(number)}" if not final else "KohLanta Discord Saison 4<br />Finale"
    title_style = styles["Title"]
    title_paragraph = Paragraph(title, title_style)
    elements.append(title_paragraph)

    text = "1. Vote"
    paragraph = Paragraph(text, styles["h2"])
    elements.append(paragraph)

    date = datetime.strptime(vote_log.date, "%d/%m/%Y %H:%M:%S")

    data = [
        [
            "Date",
            "Ouverture",
            "Fermeture",
            "Nombres de votants",
            "Votes exprimés",
            "Triches",
        ],
        [
            date.strftime("%d/%m/%Y"),
            "17h00",
            date.strftime("%Hh%M"),
            vote_log.voters_number,
            votes_number,
            vote_log.cheaters_number,
        ],
    ]
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), "#1e1f22"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (1, 1), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, "#2b2d31"),
    ]
    table = Table(data, style=table_style, hAlign="LEFT")
    elements.append(table)

    text = "2. Votes exprimés"
    paragraph = Paragraph(text, styles["h2"])
    elements.append(paragraph)

    text = "A lire comme suit:"
    custom_style = getSampleStyleSheet()["Normal"]
    custom_style.textColor = colors.whitesmoke
    custom_style.spaceBefore = 20
    last_bullet_style = getSampleStyleSheet()["Normal"]
    last_bullet_style.textColor = colors.whitesmoke
    last_bullet_style.spaceAfter = 10
    last_bullet_style.bulletIndent = 25
    last_bullet_style.leftIndent = 40
    elements.append(Paragraph(text, custom_style))
    text = html.escape("<ligne> à voté pour <colonne> à <horaire>")
    elements.append(Paragraph(text, styles["Normal"], bulletText="-"))
    if not final:
        text = html.escape("<ligne> a reçu au total <total reçu> vote(s)")
    else:
        text = html.escape("<colonne> a reçu au total <total reçu> vote(s)")
    elements.append(Paragraph(text, last_bullet_style, bulletText="-"))

    data = [["Pseudo"]]
    
    if len(players) > 8:
        data[0].append("A voté pour")
        for p in players:
            voter__id = p["_id"]
            if voter__id in votes:
                middle_content = players_username[players__id.index(votes[voter__id])]
            else: middle_content = ""
            data.append([
                p.get("nickname", "unknown"),
                middle_content,
                "",""
            ])
    elif not final:
        for p in players:
            data[0].append(p.get("nickname", "unknown"))
            middle_content = ["" for i in range(players_number + 1)]
            voter__id = p["_id"]
            if voter__id in votes:
                vote_column = players__id.index(votes[voter__id])
                middle_content[vote_column] = "X"
            data.append([p.get("nickname", "unknown")] + middle_content + [0])
    else:
        for p in players:
            data[0].append(p.get("nickname", "unknown"))
        for ep in eliminated_players:
            middle_content = ["" for i in range(players_number + 1)]
            voter__id = ep["_id"]
            if voter__id in votes:
                vote_column = players__id.index(votes[voter__id])
                middle_content[vote_column] = "X"
            data.append([ep.get("nickname", "unknown")] + middle_content)
    # [ ] vote hour
    data[0].append("Horaire")

    data[0].append("Total reçu")
    if len(players) > 8:
        for i in range(players_number): 
            data[i+1][-1] = sum(1 for row in data[1:] if row[1] == data[i+1][0])
    elif not final:
        for i in range(players_number): data[i+1][-1] = sum(1 for row in data[1:] if row[i+1] != "")
    else:
        for i in range(players_number): data[-1].append(sum(1 for row in data[1:-1] if row[i+1] != ""))

    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), "#1e1f22"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (1, 1), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), "#2ecc71"),
        ("GRID", (0, 0), (-1, -1), 1, "#2b2d31"),
    ]
    if final:
        table_style.extend([
            ("BACKGROUND", (0, -1), (-2, -1), "#1e1f22"),
            ("TEXTCOLOR", (0, -1), (-2, -1), colors.whitesmoke),
            ("ALIGN", (0, -1), (-2, -1), "CENTER"),
            ("FONTNAME", (0, -1), (-2, -1), "Helvetica-Bold"),
            ("TOPPADDING", (0, -1), (-2, -1), 6),
            ("BOTTOMPADDING", (0, -1), (-2, -1), 6),
            ("BACKGROUND", (-1, -1), (-1, -1), "#2b2d31"),
        ])
    table = Table(data, style=table_style, hAlign="LEFT")
    elements.append(table)

    text = f"3. Elimination{'s' if eliminated_at_this_vote_number>1 else ''}" if not final else "3. Victoire"
    paragraph = Paragraph(text, styles["h2"])
    elements.append(paragraph)

    if final:
        text = f"{eliminated_at_this_vote[0].nickname} a remporté cette partie de KohLanta."
    elif eliminated_at_this_vote_number == 1:
        text = f"{eliminated_at_this_vote[0].nickname} a été éliminé durant ce vote."
    elif eliminated_at_this_vote_number > 1:
        text = f"{', '.join(el.nickname for el in eliminated_at_this_vote[:-1])} et {eliminated_at_this_vote[-1].nickname} ont été éliminés durant ce vote."
    else:
        text = "Personne n'a été éliminé pendant ce vote en raison de l'utilisation d'un collier d'immunité."
    paragraph = Paragraph(text, styles["Normal"])
    elements.append(paragraph)

    text = "4. Alliances"
    paragraph = Paragraph(text, styles["h2"])
    elements.append(paragraph)

    text = f"Nombre d'alliances créées à date: {get_alliances_number()}"
    paragraph = Paragraph(text, styles["Normal"])
    elements.append(paragraph)

    if last and number != 1:
        text = "5. Joueurs éliminés"
        paragraph = Paragraph(text, styles["h2"])
        elements.append(paragraph)

        data = [["Pseudo", "Discord id", "Eliminé au vote n°"]]
        for p in eliminated_players:
            data.append(
                [
                    p.get("nickname", "unknown"),
                    p.get("id", "unknown"),
                    p.get("deathCouncilNumber", "unknown")
                ]
            )  # [ ] vote count

        table_style = [
            ("BACKGROUND", (0, 0), (-1, 0), "#1e1f22"),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("ALIGN", (1, 1), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("BACKGROUND", (0, 1), (-1, -1), "#ed4245"),
            ("GRID", (0, 0), (-1, -1), 1, "#2b2d31"),
        ]
        table = Table(data, style=table_style, hAlign="LEFT")
        elements.append(table)

    elements.append(PageBreak())

    logger.info(f"fn > render_vote > OK | number: {number} | kwargs: {kwargs}")

    return elements


def render_rules():
    logger.info(f"fn > render_rules > start")
    elements = []

    title = "KohLanta Discord Saison 4<br />Règles du jeu"
    title_style = styles["Title"]
    title_paragraph = Paragraph(title, title_style)
    elements.append(title_paragraph)

    content = "Présentation"
    elements.append(Paragraph(content, styles["h2"]))

    content = """
        Un vote est organisé tous les deux jours sur le présent serveur Discord , la personne recueillant le plus de voix est éliminée du jeu.<br />
        L'objectif est d'être le dernier joueur en jeu.<br />
        Tout est autorisé : traîtrises, alliances etc, faites vous plaisir !"
    """
    elements.append(Paragraph(content, styles["Normal"]))

    content = "Règles"
    elements.append(Paragraph(content, styles["h2"]))

    list_items = [
        "Un vote se tiendra tous les 2 jours entre 18h00 et 20h59. Les voix exprimées à 21h00 seront prises pour résultat final du vote. Ce résultat sera communiqué par Denis Brogniart dans la foulée.",
        "Chaque joueur ne dispose que d'une voix.",
        "Denis vérifiera régulièrement que vous ne votez pas pour plusieurs personnes et annulera, le cas échéant, selon les cas, le(s) dernier(s) vote(s) que vous avez exprimés ou la totalité de vos votes.",
        "S'il s'avère qu'à 21h00, lors du relevé des voix, un joueur exprime deux ou plus voix, elles seront toutes annulées.",
        "Pour que le résultat d’un vote soit pris en compte, la majorité des joueurs restants doivent avoir voté.",
        "En cas d'égalité, le dernier joueur éliminé aura le dernier mot. Les modalités de vote",
        "Le dernier vote (lors de la finale) est ouvert à tous les éliminés et dure du 8h00 à 20h59. A partir de l’ouverture de ce vote, les finalistes se voient retirer leur droit de parole sur l’ensemble des salons.",
        "Une fois éliminé, les personnes ne peuvent plus participer aux votes, ne peuvent plus interagir sur le groupe de discussion général, peuvent interagir sur le groupe des éliminés.",
        "Un système de collier d’immunité a été mis en place. En voici les règles :",
        [
            "Un smiley :collierimmunite:  est dissimulé quelque part sur le serveur, dans une discussion accessible à tous les joueurs restants, à une date tenue secrète.",
            "Toute personne qui trouve le smiley :collierimmunite:  est enjoint à cliquer dessus au plus vite. Ce dernier disparaitra de façon quasi instantanée. Dès à présent, vous êtes détenteur (de façon secrète) du collier d’immunité.",
        ],
        "Le collier d'immunité est utilisé automatiquement après un vote dont vous êtes le perdant, les votes contre vous ne sont alors pas comptabilisés. Ce dispositif ne fonctionne qu’une seule fois. Vous conservez le collier tant qu’il n’a pas servi à vous protéger d’une expulsion par un vote.",
        "Le collier d’immunité n’a aucun effet en finale.",
    ]
    subitem_style = getSampleStyleSheet()["Normal"]
    subitem_style.textColor = colors.whitesmoke
    subitem_style.bulletIndent = 50
    subitem_style.leftIndent = 65
    for item in list_items:
        if type(item) == str:
            elements.append(Paragraph(item, styles["Normal"], bulletText="-"))
        elif type(item) == list:
            for subitem in item:
                elements.append(Paragraph(subitem, subitem_style, bulletText="¤"))

    content = "Le maître du jeu peut à tout moment modifier les règles précédentes, et le jeu peut de lui-même vous faire transgresser ces règles, mais cela vous sera alors indiqué. "
    elements.append(Paragraph(content, styles["Normal"]))

    content = "Précédents vainqueurs"
    elements.append(Paragraph(content, styles["h2"]))

    elements.append(Paragraph("Saison 1: Marius S.", styles["Normal"], bulletText="-"))
    elements.append(Paragraph("Saison 2: Ewan M.", styles["Normal"], bulletText="-"))
    elements.append(Paragraph("Saison 3: Augustin V.", styles["Normal"], bulletText="-"))

    logger.info(f"fn > render_rules > OK")

    return elements


def generate(vote_number,**kwargs) -> str:
    vote_number = 50 if vote_number > 50 else vote_number
    logger.info(f"fn > generate > start | vote_number: {vote_number}")
    name = f"KohLantaVote{str(vote_number)}.pdf"
    create_pdf(f"pdf/{name}", vote_number, **kwargs)
    logger.info(f"fn > generate > OK | vote_number: {vote_number} | PDF name: {name}")
    if os.name == "posix":
        return f"{DIRNAME}/pdf/{name}"
    else:
        return f"{DIRNAME}\\pdf\\{name}"


logger.info(f"Ready")
