"""Check physical artifacts and saved outputs on the integrated worktree."""
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1]).resolve()
projects = {
    'economics': '01-economics-and-econometrics/01-macroeconomics/01-strategic-monetary-transmission/inflation-bias-audit',
    'math': '02-mathematics-statistics-and-quant/quant-libraries/streaming-moments',
    'risk': '03-financial-risk/01-credit-risk/credit-risk-products/competing-exit-loss-audit',
    'ai': '05-artificial-intelligence-and-computational-systems/02-machine-learning-engineering/mvp-linked-entity-holdout',
    'ceo': '06-strategy-innovation-and-leadership/21-executive-governance-board-decisions/quorum-common-cause-gate',
}
result = {}
for name, relative in projects.items():
    project = root / relative
    required = ['README.md', 'MVP.md', 'requirements.txt', 'referencias.bib', 'src', 'tests', 'results']
    assert all((project / p).exists() for p in required), name
    references = len(re.findall(r'(?m)^@', (project / 'referencias.bib').read_text()))
    assert references >= 5, (name, references)
    notebooks = []
    for p in project.glob('*.ipynb'):
        n = json.loads(p.read_text())
        cells = [c for c in n['cells'] if c['cell_type'] == 'code']
        assert cells and all(c.get('execution_count') is not None for c in cells), p
        assert not any(o.get('output_type') == 'error' for c in cells for o in c.get('outputs', [])), p
        notebooks.append({'path': p.name, 'code_cells': len(cells), 'outputs': sum(len(c.get('outputs', [])) for c in cells)})
    assert notebooks
    assert list((project / 'results').rglob('*.csv'))
    assert list((project / 'results').rglob('*.json'))
    assert list((project / 'results').rglob('*.png'))
    result[name] = {'path': relative, 'required_present': required, 'bib_entries': references, 'notebooks': notebooks}
print(json.dumps(result, indent=2))
