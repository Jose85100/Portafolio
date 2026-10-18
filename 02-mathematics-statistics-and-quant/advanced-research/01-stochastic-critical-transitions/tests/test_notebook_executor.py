import nbformat
import pytest

from scripts_notebook import execute_in_process


def test_executor_captures_real_output_and_rejects_errors():
    nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("print(2 + 3)")])
    execute_in_process(nb)
    assert nb.cells[0].outputs[0].text == "5\n"
    assert nb.cells[0].execution_count == 1
    nbformat.validate(nb)
    broken = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("raise ValueError('audit test')")])
    with pytest.raises(RuntimeError, match="Notebook cell failed"):
        execute_in_process(broken)
