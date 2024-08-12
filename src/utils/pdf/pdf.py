import os

from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

from utils.logging import get_logger

from database.votelog import VoteLogList

from .common import DIRNAME
from .rulesPage import RulesPage
from .votePage import VotePage

logger = get_logger(__name__)

logger.info('Setup running...')


# [ ] add tied_players section


def background_canvas(canvas_obj, doc):
    """Set the background color of the PDF."""

    canvas_obj.saveState()
    canvas_obj.setFillColor('#2b2d31')
    canvas_obj.rect(0, 0, A4[0], A4[1], fill=True, stroke=False)
    canvas_obj.restoreState()


def create_pdf(file_path, vote_number, **kwargs):
    """Create a PDF file."""

    logger.info(f'create_pdf > start | file_path: {file_path} | vote_number: {vote_number}')
    doc = BaseDocTemplate(file_path, pagesize=A4, leftMargin=50, title=f'KohLanta Saison 4 - Vote {vote_number}')

    elements = []

    frame = Frame(0, 0, A4[0], A4[1], 50, 30, 50, 30, showBoundary=1)
    background_template = PageTemplate(
        id='background1', frames=[frame], onPage=background_canvas
    )
    doc.addPageTemplates([background_template])

    vote_logs = VoteLogList()

    pages = [VotePage(vote_number, vote_logs, last=True, **kwargs)]

    if vote_number > 1:
        pages.extend([VotePage(vote, vote_logs) for vote in range(vote_number - 1, 0, -1)])
    pages.append(RulesPage())
    for page in pages:
        elements.extend(page.elements)

    doc.build(elements)
    logger.info(f'create_pdf > OK | file_path: {file_path} | vote_number: {vote_number}')


def generate(vote_number, **kwargs) -> str:
    """Generate a PDF file."""

    vote_number = 50 if vote_number > 50 else vote_number
    logger.info(f'fn > generate > start | vote_number: {vote_number}')
    name = f'KohLantaVote{str(vote_number)}.pdf'
    create_pdf(f'pdf/{name}', vote_number, **kwargs)
    logger.info(f'fn > generate > OK | vote_number: {vote_number} | PDF name: {name}')
    if os.name == 'posix':
        return f'{DIRNAME}/pdf/{name}'
    else:
        return f'{DIRNAME}\\pdf\\{name}'


async def remove_files() -> None:
    """Delete the PDF files."""

    logger.info('fn > delete_files > start')
    for pdf_file in DIRNAME.rglob('*.pdf'):
        os.remove(pdf_file)
        logger.info(f'delete_files > removed: {pdf_file}')
    logger.info('fn > delete_files > OK')


logger.info('Ready')
