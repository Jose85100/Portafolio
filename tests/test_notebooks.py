"""Ejecuta cada notebook del repositorio de principio a fin.

Un notebook falla si alguna celda lanza una excepcion, incluidos los `assert`
de su seccion de pruebas. Uso:

    python3 -m unittest tests.test_notebooks -v
"""
import pathlib
import unittest

import nbformat
from nbclient import NotebookClient

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def _crear_prueba(ruta):
    def prueba(self):
        nb = nbformat.read(ruta, as_version=4)
        NotebookClient(nb, timeout=1800, kernel_name="python3",
                       resources={"metadata": {"path": str(ruta.parent)}}).execute()
    return prueba


class PruebasDeNotebooks(unittest.TestCase):
    pass


for _nb in sorted(RAIZ.rglob("*.ipynb")):
    _nombre = "test_" + "_".join(_nb.relative_to(RAIZ).with_suffix("").parts).replace("-", "_")
    setattr(PruebasDeNotebooks, _nombre, _crear_prueba(_nb))

if __name__ == "__main__":
    unittest.main()
