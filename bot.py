import sys
from subprocess import call
from src.utils.logging import get_logger

logger = get_logger(__name__)

arg = sys.argv[1] if len(sys.argv) > 1 else None

match arg:
    case 'run':
        try:
            call(['python', 'src/main.py'])
        except KeyboardInterrupt:
            exit()
    case 'flake':
        try:
            call(['python', 'src/flake8.py'])
        except KeyboardInterrupt:
            exit()
    case 'lines_count':
        try:
            call(['python', 'src/lines_count.py'])
        except KeyboardInterrupt:
            exit()
    case _:
        logger.warning('\nNo action specified.\nPlease choose between: run, flake, lines_count')
