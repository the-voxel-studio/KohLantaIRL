import os


def compte_lignes_code(directory):
    """Compte le nombre de lignes de code dans les fichiers .py"""
    total_lignes = 0

    for root, dirs, files in os.walk(directory):
        # Exclure le dossier .venv
        if '.venv' in dirs:
            dirs.remove('.venv')

        for fichier in files:
            if fichier.endswith('.py'):
                chemin_fichier = os.path.join(root, fichier)
                with open(chemin_fichier, 'r', encoding='utf-8') as f:
                    lignes = f.readlines()
                    total_lignes += len(lignes)
                    print(f"Le fichier {chemin_fichier.split('KohLanta')[-1]} contient {len(lignes)} lignes.")

    return total_lignes


repertoire_a_analyser = os.getcwd()

nombre_lignes = compte_lignes_code(repertoire_a_analyser)
print(f'Total of lines (venv excepted) : {nombre_lignes}')
