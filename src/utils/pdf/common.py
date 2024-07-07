from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

DIRNAME = Path(__file__).parent.parent.parent.parent

styles = getSampleStyleSheet()
styles['Title'].textColor = colors.whitesmoke
styles['h1'].textColor = colors.red
styles['h2'].textColor = colors.whitesmoke
styles['h3'].textColor = colors.whitesmoke
styles['Normal'].textColor = colors.whitesmoke
styles['Normal'].bulletIndent = 25
styles['Normal'].leftIndent = 40
