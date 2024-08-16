from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

from utils.logging import get_logger

from .common import styles

logger = get_logger(__name__)


class RulesPage:
    """Class for the rules page."""

    def __init__(self) -> None:
        """Init the class."""

        self.elements = []
        self._header = Paragraph(
            'KohLanta Discord Saison 4<br />Règles du jeu',
            styles['Title']
        )

        self._render()

    @property
    def _presentation_section(self):
        """Set the presentation section elements."""

        elements = []

        content = 'Présentation'
        elements.append(Paragraph(content, styles['h2']))

        content = """
            Un vote est organisé tous les deux jours sur le présent serveur Discord , la personne recueillant le plus de voix est éliminée du jeu.<br />
            L'objectif est d'être le dernier joueur en jeu.<br />
            Tout est autorisé: traîtrises, alliances etc, faites vous plaisir !'
        """
        elements.append(Paragraph(content, styles['Normal']))
        return elements

    @property
    def _rules_section(self):
        """Set the rules section elements."""

        elements = []

        content = 'Règles'
        elements.append(Paragraph(content, styles['h2']))

        list_items = [
            'Un vote se tiendra tous les 2 jours entre 18h00 et 20h59. Les voix exprimées à 21h00 seront prises pour résultat final du vote. Ce résultat sera communiqué par Denis Brogniart dans la foulée.',
            "Chaque joueur ne dispose que d'une voix.",
            'Denis vérifiera régulièrement que vous ne votez pas pour plusieurs personnes et annulera, le cas échéant, selon les cas, le(s) dernier(s) vote(s) que vous avez exprimés ou la totalité de vos votes.',
            "Si il s'avère qu'à 21h00, lors du relevé des voix, un joueur exprime deux ou plus voix, elles seront toutes annulées.",
            'Pour que le résultat d’un vote soit pris en compte, la majorité des joueurs restants doivent avoir voté.',
            "En cas d'égalité, le dernier joueur éliminé aura le dernier mot. Les modalités de vote",
            'Le dernier vote (lors de la finale) est ouvert à tous les éliminés et dure du 8h00 à 20h59. A partir de l’ouverture de ce vote, les finalistes se voient retirer leur droit de parole sur l’ensemble des salons.',
            'Une fois éliminé, les personnes ne peuvent plus participer aux votes, ne peuvent plus interagir sur le groupe de discussion général, peuvent interagir sur le groupe des éliminés.',
            'Un système de collier d’immunité a été mis en place. En voici les règles:',
            [
                'Un smiley :collierimmunite: est dissimulé quelque part sur le serveur, dans une discussion accessible à tous les joueurs restants, à une date tenue secrète.',
                'Toute personne qui trouve le smiley:collierimmunite:  est enjoint à cliquer dessus au plus vite. Ce dernier disparaitra de façon quasi instantanée. Dès à présent, vous êtes détenteur (de façon secrète) du collier d’immunité.',
            ],
            "Le collier d'immunité est utilisé automatiquement après un vote dont vous êtes le perdant, les votes contre vous ne sont alors pas comptabilisés. Ce dispositif ne fonctionne qu’une seule fois. Vous conservez le collier tant qu’il n’a pas servi à vous protéger d’une expulsion par un vote.",
            'Le collier d’immunité n’a aucun effet en finale.',
        ]
        subitem_style = getSampleStyleSheet()['Normal']
        subitem_style.textColor = colors.whitesmoke
        subitem_style.bulletIndent = 50
        subitem_style.leftIndent = 65
        for item in list_items:
            if isinstance(item, str):
                elements.append(Paragraph(item, styles['Normal'], bulletText='-'))
            elif isinstance(item, list):
                for subitem in item:
                    elements.append(Paragraph(subitem, subitem_style, bulletText='¤'))

        content = 'Le maître du jeu peut à tout moment modifier les règles précédentes, et le jeu peut de lui-même vous faire transgresser ces règles, mais cela vous sera alors indiqué. '
        elements.append(Paragraph(content, styles['Normal']))

        return elements

    @property
    def _previous_winners_section(self):
        """Set the previous winners section elements."""

        elements = []

        content = 'Précédents vainqueurs'
        elements.append(Paragraph(content, styles['h2']))

        elements.append(Paragraph('Saison 1: Marius S.', styles['Normal'], bulletText='-'))
        elements.append(Paragraph('Saison 2: Ewan M.', styles['Normal'], bulletText='-'))
        elements.append(Paragraph('Saison 3: Augustin V.', styles['Normal'], bulletText='-'))
        elements.append(Paragraph('Saison 4: Armand W.', styles['Normal'], bulletText='-'))

        return elements

    def _render(self):
        """Set each sections."""

        self.elements.append(self._header)
        self.elements.extend(self._presentation_section)
        self.elements.extend(self._rules_section)
        self.elements.extend(self._previous_winners_section)
        logger.info('rules_page rendering > OK')
