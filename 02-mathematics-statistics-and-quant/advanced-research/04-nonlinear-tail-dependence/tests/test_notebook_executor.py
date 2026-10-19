import nbformat
import pytest

from scripts_notebook import execute_in_process


def test_actual_execution_and_error_propagation():
    notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("print(7*6)")])
    execute_in_process(notebook)
    assert notebook.cells[0].outputs[0].text == "42\n"
    nbformat.validate(notebook)
    broken = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("raise ValueError('test')")])
    with pytest.raises(RuntimeError, match="Notebook cell failed"):
        execute_in_process(broken)
