import nbformat
import pytest
from scripts_notebook import execute_in_process


def test_executor_records_real_output():
    nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("print(6*7)")])
    result = execute_in_process(nb)
    assert "42" in result.cells[0].outputs[0].text
    assert result.cells[0].execution_count == 1


def test_executor_fails_on_error():
    nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("raise ValueError('intentional')")])
    with pytest.raises(RuntimeError):
        execute_in_process(nb)


def test_executor_records_rich_output():
    nb = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_code_cell(
                "from IPython.display import display, HTML; display(HTML('<b>verified</b>'))"
            )
        ]
    )
    result = execute_in_process(nb)
    assert any("text/html" in o.get("data", {}) for o in result.cells[0].outputs)
