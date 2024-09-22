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
            Qui n'a jamais rêvé de participer à Koh-Lanta avec ses amis ? De participer à des épreuves, former des alliances, et bien évidemment voter pour éliminer l'un d'entre eux.<br/>
            Ce serveur Discord est entièrement géré par Denis Brogniart (un bot encore mieux que le vrai), êtes vous prêt à vivre cette aventure tous ensemble ? Affrontez-vous dans des épreuves à distance. Formez plusieurs équipes pour des soirées encore plus intenses et battez vous pour être le dernier survivant.<br/>
            L'occasion parfaite de faire ressortir de vieilles rancœurs, de trahir ses plus fidèles amis et de former de nombreuses alliances en jouant sur plusieurs tableaux. Ne manquez pas les conseils du soir où chaque vote compte !<br/>
            Vivez des moments de tension et de complicité qui testeront vos amitiés comme jamais auparavant.<br/>
            Un vote est organisé chaque jour et toutes les fourberies sont autorisés.<br/>
            La personne recueillant le plus de voix est éliminée du jeu, et la sentence est bien évidément irrévocable.
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
            'Un vote se tiendra tous les jours entre 17h00 et 20h59. Les voix exprimées à 21h00 seront prises comme résultat final du vote. Ce résultat sera communiqué par Denis Brogniart dans la foulée.',
            'Vous pouvez créer des alliances tenues secrètes ! Leur fonctionnement est expliqué dans le salon <#1139247647107067914>.',
            "Sauf pouvoir temporaire, chaque joueur ne dispose que d'une voix par vote. (explications plus bas)",
            'Denis vérifiera régulièrement que vous ne votez pas pour plusieurs personnes et annulera, le cas échéant, le(s) dernier(s) vote(s) que vous avez exprimés.',
            "S'il s'avère qu'à 21h00, lors du relevé des voix, un joueur exprime deux voix ou plus, elles seront toutes annulées.",
            "En cas d'égalité, ce sera au dernier joueur éliminé de décider. Il a pour cela jusqu'à 14h le lendemain du vote ayant amené à une égalité.",
            "Le dernier vote (lors de la finale) est ouvert à tous les éliminés et dure de 8h00 à 20h59. À partir de l'ouverture de ce vote, les finalistes se voient retirer leur droit de parole sur l’ensemble des salons.",
            'Une fois éliminés, les personnes ne peuvent plus participer aux votes, ne peuvent plus interagir sur le salon de discussion général, mais peuvent interagir au sein du salon des éliminés',
            'Les modérateurs se réservent le droit d’éliminer/muter un joueur si son comportement n’est pas respectueux.',
            'Les modérateurs ne sont pas au dessus des règles, un comportement abusif pourra être sanctionné.',
            'Un système de collier d’immunité a été mis en place. Voici les règles :',
            [
                'Un smiley <:collierimmunite:1145354940705943652> sera dissimulé dans le channel Général, accessible à tous les joueurs restants, à une date tenue secrète.',
                'Toute personne qui trouve le smiley <:collierimmunite:1145354940705943652> est invitée à cliquer dessus au plus vite. Ce dernier disparaîtra de façon quasi instantanée. Dès à présent, vous êtes détenteur (de façon secrète) du collier d’immunité.',
                "Le collier d'immunité est utilisé automatiquement après un vote dont vous êtes le perdant. Les votes contre vous ne sont alors pas comptabilisés. Ce dispositif ne fonctionne qu’une seule fois. Vous conservez le collier tant qu’il n’a pas servi à vous protéger d’une expulsion par un vote.",
                "Le collier d'immunité n’a aucun effet en finale.",
                "Le collier n'apparaîtra qu'une seule fois sur l'ensemble de la partie.",
                "Ce collier est différent du \"pouvoir temporaire d'immunitée\""
            ]
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

        content = 'Le maître du jeu peut à tout moment modifier les règles précédentes, et le jeu peut de lui-même vous faire transgresser ces règles, mais cela vous sera alors indiqué.'
        elements.append(Paragraph(content, styles['Normal']))

        return elements

    @property
    def _news_section(self):
        """Set the news section elements."""

        elements = []

        content = 'Nouveautés'
        elements.append(Paragraph(content, styles['h2']))

        list_items = [
            'Une fois éliminé, votre partie n’est pas finie pour autant. Votre participation sera encore nécessaire lors de la finale notamment !',
            "Plusieurs canaux de discussions vocales sont ouverts. N'hésitez pas à vous y rejoindre, cela reste un jeu entre amis. Profitez !",
            'Vous pouvez dorénavant parler avec Denis Brogniart en MP, mais le comprendrez vous ?',
            "Si vous êtes éliminé, vous aurez 24h pour envoyer votre dernière parole à Denis Brogniart, qui l'enverra sur le salon général. Une fois fait, vous ne pourrez plus discuter là-bas.",
            'À chaque fin de vote, Denis Brogniart regroupera toutes les informations de celui-ci sur un fichier PDF qui vous sera mis à disposition.',
            "Certains vote seront aléatoirement anonyme, pas de noms sur le PDF. L'occasion rêvée de trahir ces amis !",
            "En cas d'égalité au premier vote, toutes les personnes étant à égalité seront éliminées.",
            'Certains jours, des mini jeux seront lancés par Denis Brogniart. Donnant droit à des récompenses pour le/les gagnants :',
            [
                'Immunité : le joueur sera immunisé au vote suivant seulement.',
                'Double vote : le prochain vote du joueur comptera double.',
                "/pouvoir mute : le joueur aura l'autorisation de mute un autre survivant durant une période donnée",
                '/pouvoir block : le joueur choisira à sa guise, un survivant qui ne pourra pas voter au prochain conseil.',
                "/pouvoir resurrect : le joueur à la possibilité de faire revenir à la vie l'un des éliminés.",
                "Nothing : pas de chance pour le joueur qui n'obtient aucune récompenses."
            ]
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
        self.elements.extend(self._news_section)
        self.elements.extend(self._previous_winners_section)
        logger.info('rules_page rendering > OK')
