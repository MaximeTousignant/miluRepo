"""Réexécute tous les notebooks de phys/ et enregistre leurs sorties en place.

Depuis la racine du repo :
    uv run phys/executer.py              # tous les notebooks
    uv run phys/executer.py univers-5d   # un seul sujet
"""
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

PHYS = Path(__file__).resolve().parent


def executer(chemin: Path) -> None:
    nb = nbformat.read(chemin, as_version=4)
    NotebookClient(nb, timeout=600, kernel_name="python3",
                   resources={"metadata": {"path": str(chemin.parent)}}).execute()
    nbformat.write(nb, chemin)
    print(f"ok  {chemin.relative_to(PHYS)}")


if __name__ == "__main__":
    sujets = sys.argv[1:] or ["*"]
    for sujet in sujets:
        for chemin in sorted(PHYS.glob(f"{sujet}/*.ipynb")):
            executer(chemin)
