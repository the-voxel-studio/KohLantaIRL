import html
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (PageBreak, Paragraph, Table)

from database.player import PlayerList
from database.votelog import VoteLogList
from utils.logging import get_logger

from .common import styles

logger = get_logger(__name__)


class VotePage:
    """Classe for the vote page."""

    def __init__(self, number: int, vote_logs: VoteLogList, **kwargs) -> None:
        """Init the class."""

        self.number = number
        self._final = kwargs.get('final', False)
        self._vote_logs = vote_logs
        self._vote_log = self._vote_logs.objects[number - 1]
        self._votes_number = len(self._vote_log.object.votes)
        self._players = PlayerList(alive=True).objects
        self._votes = {v['voter'].object._id: v['for'].object._id for v in self._vote_log.object.votes}
        self._eliminated_players = PlayerList(alive=False).objects
        self._eliminated_at_this_vote = self._vote_log.object.eliminated
        self._eliminated_at_this_vote_number = len(self._eliminated_at_this_vote)
        if not self._final:
            self._in_vote_living_participants = [el for el in self._eliminated_players if el.object.death_council_number >= number]
            self._players.extend(self._in_vote_living_participants)
        self._players_number = len(self._players)
        self._players__id = [p.object._id for p in self._players]
        self._players_username = [p.object.nickname for p in self._players]
        self._last = kwargs.get('last', False)

        self.elements = []
        self._header = Paragraph(
            f'KohLanta Discord Saison 4<br />Vote n°{str(number)}'
            if not self._final else 'KohLanta Discord Saison 4<br />Finale',
            styles['Title']
        )
        self._anonymous_section = Paragraph('Ce vote était anonyme', styles['h1'])

        self._render()

    @property
    def _presentation_section(self):
        """Set the presentation section elements."""

        elements = []

        text = '1. Vote'
        paragraph = Paragraph(text, styles['h2'])
        elements.append(paragraph)

        date = datetime.strptime(self._vote_log.object.date, '%d/%m/%Y %H:%M:%S')

        data = [  # Tout ce qui est en lien avec le tableau du pdf.
            [
                'Date',
                'Ouverture',
                'Fermeture',
                'Nombres de votants',
                'Votes exprimés',
                'Triches',
            ],
            [
                date.strftime('%d/%m/%Y'),
                '17h00',
                date.strftime('%Hh%M'),
                self._vote_log.object.voters_number,
                self._votes_number,
                self._vote_log.object.cheaters_number,
            ],
        ]
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), '#1e1f22'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, '#2b2d31'),
        ]
        table = Table(data, style=table_style, hAlign='LEFT')
        elements.append(table)

        return elements

    @property
    def _vote_section(self):
        """Set the vote section elements."""

        elements = []

        text = '2. Votes exprimés'
        paragraph = Paragraph(text, styles['h2'])
        elements.append(paragraph)

        text = 'A lire comme suit:'
        custom_style = getSampleStyleSheet()['Normal']
        custom_style.textColor = colors.whitesmoke
        custom_style.spaceBefore = 20
        last_bullet_style = getSampleStyleSheet()['Normal']
        last_bullet_style.textColor = colors.whitesmoke
        last_bullet_style.spaceAfter = 10
        last_bullet_style.bulletIndent = 25
        last_bullet_style.leftIndent = 40
        elements.append(Paragraph(text, custom_style))
        text = html.escape('<ligne> à voté pour <colonne> à <horaire>')
        elements.append(Paragraph(text, styles['Normal'], bulletText='-'))
        if not self._final:
            text = html.escape('<ligne> a reçu au total <total reçu> vote(s)')
        else:
            text = html.escape('<colonne> a reçu au total <total reçu> vote(s)')
        elements.append(Paragraph(text, last_bullet_style, bulletText='-'))

        data = [['Pseudo']]

        if len(self._players) > 8:
            data[0].append('A voté pour')
            for p in self._players:
                voter__id = p['_id']
                if voter__id in self._votes:
                    middle_content = self._players_username[self._players__id.index(self._votes[voter__id])]
                else:
                    middle_content = ''
                data.append([
                    p.get('nickname', 'unknown'),
                    middle_content,
                    '',
                    ''
                ])
        elif not self._final:
            for p in self._players:
                data[0].append(p.object.nickname)
                middle_content = ['' for i in range(self._players_number + 1)]
                voter__id = p.object._id
                if voter__id in self._votes:
                    vote_column = self._players__id.index(self._votes[voter__id])
                    middle_content[vote_column] = 'X'
                data.append([p.object.nickname] + middle_content + [0])
        else:
            for p in self._players:
                data[0].append(p.object.nickname)
            for ep in self._eliminated_players:
                middle_content = ['' for i in range(self._players_number + 1)]
                voter__id = ep.object._id
                if voter__id in self._votes:
                    vote_column = self._players__id.index(self._votes[voter__id])
                    middle_content[vote_column] = 'X'
                data.append([ep.object.nickname] + middle_content)
        # [ ] vote hour
        data[0].append('Horaire')

        if not self._final:
            data[0].append('Total reçu')
            if len(self._players) > 8:
                for i in range(self._players_number):
                    data[i + 1][-1] = sum(1 for row in data[1:] if row[1] == data[i + 1][0])
            else:
                for i in range(self._players_number):
                    data[i + 1][-1] = sum(1 for row in data[1:] if row[i + 1] != '')
        else:
            data.append(['Total reçu'])
            for i in range(self._players_number):
                data[-1].append(sum(1 for row in data[1:-1] if row[i + 1] != ''))

        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), '#1e1f22'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), '#2ecc71'),
            ('GRID', (0, 0), (-1, -1), 1, '#2b2d31'),
        ]
        if self._final:
            table_style.extend([
                ('BACKGROUND', (0, -1), (-2, -1), '#1e1f22'),
                ('TEXTCOLOR', (0, -1), (-2, -1), colors.whitesmoke),
                ('ALIGN', (0, -1), (-2, -1), 'CENTER'),
                ('FONTNAME', (0, -1), (-2, -1), 'Helvetica-Bold'),
                ('TOPPADDING', (0, -1), (-2, -1), 6),
                ('BOTTOMPADDING', (0, -1), (-2, -1), 6),
                ('BACKGROUND', (-1, -1), (-1, -1), '#2b2d31'),
            ])
        table = Table(data, style=table_style, hAlign='LEFT')
        elements.append(table)

        return elements

    @property
    def _current_vote_eliminations_section(self):
        """Set the eliminations section elements."""

        elements = []

        text = f"{'2' if self._vote_log.object.hidden else '3'}. Elimination{'s' if self._eliminated_at_this_vote_number>1 else ''}" if not self._final else '2. Victoire'  # Juste pour changer le chiffre
        paragraph = Paragraph(text, styles['h2'])
        elements.append(paragraph)

        if self._final:
            text = f'{self._eliminated_at_this_vote.objects[0].object.nickname} a remporté cette partie de KohLanta.'
        elif self._eliminated_at_this_vote_number == 1:
            text = f'{",".join([p.object.nickname for p in self._eliminated_at_this_vote.objects])} a été éliminé durant ce vote.'
        elif self._eliminated_at_this_vote_number > 1:
            text = f"{', '.join(el.object.nickname for el in self._eliminated_at_this_vote.objects[:-1])} et {self._eliminated_at_this_vote.objects[-1].object.nickname} ont été éliminés durant ce vote."
        else:
            text = "Personne n'a été éliminé pendant ce vote en raison de l'utilisation d'un collier d'immunité."
        paragraph = Paragraph(text, styles['Normal'])
        elements.append(paragraph)

        return elements

    @property
    def _alliances_section(self):
        """Set the alliances section elements."""

        elements = []

        text = f'{"3" if self._vote_log.object.hidden else "4"}. Alliances'
        paragraph = Paragraph(text, styles['h2'])
        elements.append(paragraph)

        text = f"Nombre d'alliances créées à date: {self._vote_log.object.alliance_number if self._vote_log.object.alliance_number else 'inconnu'}"
        paragraph = Paragraph(text, styles['Normal'])
        elements.append(paragraph)

        return elements

    @property
    def all_votes_eliminations_section(self):
        """Set the eliminations section elements."""

        elements = []

        text = f'{"4" if self._vote_log.object.hidden else "5"}. Joueurs éliminés'
        paragraph = Paragraph(text, styles['h2'])
        elements.append(paragraph)

        data = [['Pseudo', 'Eliminé au vote n°', 'Votes reçus', 'Proportion']]
        for p in sorted(self._eliminated_players, key=lambda x: x.object.death_council_number):
            death_vote_log = self._vote_logs.objects[p.object.death_council_number - 1]
            nb_received_votes = sum([1 for vote in death_vote_log.object.votes if vote["for"].object.id == p.object.id])
            nb_cast_votes = len(death_vote_log.object.votes)
            percentage_received = round(nb_received_votes / nb_cast_votes * 100, 2)
            data.append(
                [
                    p.object.nickname,
                    p.object.death_council_number,
                    f'{nb_received_votes}/{nb_cast_votes}',
                    f'{percentage_received}%'
                ]
            )  # [ ] vote count (n/n + %)

        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), '#1e1f22'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), '#ed4245'),
            ('GRID', (0, 0), (-1, -1), 1, '#2b2d31'),
        ]
        table = Table(data, style=table_style, hAlign='LEFT')
        elements.append(table)

        return elements

    def _render(self) -> None:
        """Set each sections."""

        self.elements.append(self._header)
        if self._vote_log.object.hidden:
            self.elements.append(self._anonymous_section)
        self.elements.extend(self._presentation_section)
        if not self._vote_log.object.hidden:
            self.elements.extend(self._vote_section)
        self.elements.extend(self._current_vote_eliminations_section)
        self.elements.extend(self._alliances_section)
        if self._last and self.number != 1:
            self.elements.extend(self.all_votes_eliminations_section)
        self.elements.append(PageBreak())
        logger.info(f'vote_page rendering > OK | vote_number: {self.number}')
