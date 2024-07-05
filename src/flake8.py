import subprocess


def run_flake8(directory, exclude=[]):
    """
    Run Flake8 in the specified directory and its subdirectories,
    excluding files and directories specified in the 'exclude' list.
    """

    command = ['flake8']
    command.extend([f"--exclude={','.join(exclude)}"])
    command.extend(['--show-source'])
    command.extend([f"--extend-ignore={','.join(['E402', 'E501'])}"])
    command.append(directory)

    try:
        subprocess.run(command, check=True)
        print('Flake8 a été exécuté avec succès.')

    except subprocess.CalledProcessError:
        print("Au moins une erreur lors de l'exécution de Flake8.")


if __name__ == '__main__':

    directory_to_check = '.'

    files_and_dirs_to_exclude = [
        '.venv',
        '.git',
        'backup',
        '__pycache__',
        'flake8.py',
        'lines_count.py',
        '__init__.py'
    ]

    run_flake8(directory_to_check, files_and_dirs_to_exclude)
