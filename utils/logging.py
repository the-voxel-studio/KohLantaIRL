import logging

from colorama import Fore, Style

# LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
CONSOLE_LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
FILE_LOG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        'DEBUG': Fore.GREEN,
        'INFO': Fore.BLUE,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA,
    }

    def format(self, record):
        levelname = record.levelname
        colored_levelname = f'{self.LEVEL_COLORS.get(levelname, Fore.WHITE)}{Style.BRIGHT}{levelname}{Style.RESET_ALL}'

        levelname_length = len(levelname)
        spacing = ' ' * (8 - levelname_length)

        name = record.name
        colored_name = f'{Fore.MAGENTA}{name}{Style.RESET_ALL}'

        formatted_message = self._fmt % {
            'levelname': colored_levelname + spacing,
            'name': colored_name,
            'message': record.getMessage(),
            'asctime': self.formatTime(record, self.datefmt),
        }
        formatted_message = formatted_message.replace('{levelname}', colored_levelname + spacing)
        formatted_message = formatted_message.replace('{name}', colored_name)

        return formatted_message
    
class FileFormatter(logging.Formatter):
    def format(self, record):
        levelname_length = len(record.levelname)
        spacing = ' ' * (8 - levelname_length)

        formatted_message = self._fmt % {
            'levelname': record.levelname + spacing,
            'name': record.name,
            'message': record.getMessage(),
            'asctime': self.formatTime(record, self.datefmt),
        }
        formatted_message = formatted_message.replace('{levelname}', record.levelname + spacing)

        return formatted_message

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter(CONSOLE_LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler('logs/bot.log')
    file_handler.setFormatter(FileFormatter(FILE_LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    logger.addHandler(file_handler)

    if name == "__main__":
        discord_logger = logging.getLogger('discord')
        discord_logger.addHandler(file_handler)

    return logger