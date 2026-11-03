"""Generate and execute the audit-envelope teaching notebook in a fresh process."""

from pathlib import Path

import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parent
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {"name": "python3", "display_name": "Python 3", "language": "python"}
nb.metadata.execution = {
    "executor": "IPython in-process, fresh process, sequential abort-on-error",
    "scope": "no isolated Jupyter kernel claimed",
}
nb.cells = [
    md("""# Integridad de summaries: metadatos laterales sin alterar el wire

## Pregunta, utilidad y continuidad del programa

El laboratorio desarrolla Welford desplazado, escalado, autoescala y fusión Chan; el 2-nov se añadió un payload numérico `MOMENTS_V1` que consume C++20. Ese contrato transporta suficientes estadísticas pero omite historial de diagnósticos. Si el consumidor reinicia un contador a cero, ¿cómo distinguir el cero medido de desconocido sin modificar las siete columnas numéricas? El valor práctico es revisar una exportación sin atribuir propiedades que no están en los datos.

## Fórmula, unidades y alcance

Para valores `x` con unidad U, el normalizador usa `y=x/2^e`; `a` y `b` están en unidades de `y`, y `Q=Σ(y−(a+b))²`. La varianza calculada sigue siendo `s_d²=2^(2e) Q/(n−d)`, `d∈{0,1}`, `n>d`; su unidad es U². El sobre no cambia `n,e,a,b,Q` ni el estimador. No hay nueva derivación estadística.

H1 fijada antes del experimento: 12/12 payloads y categorías diagnósticas round-trip exactos. H2: una mutación de payload o metadata sin recalcular digest falla. El benchmark compara envelope estructurado contra un JSON sidecar plano con **la misma información y ambos hashes**; no se predice superioridad temporal."""),
    code("""import json
from pathlib import Path
from IPython.display import display, Image
from src.audit_envelope import create_envelope, dumps_envelope, loads_envelope
from src.transport import export_state
from src.dynamic import DynamicMoments

cfg = json.loads(Path('config_envelope.json').read_text())
cfg"""),
    md("""## Semántica de disponibilidad

`tracked` contiene todos los contadores enteros, y el cero significa medido. `partial` contiene un subconjunto propio de contadores; los demás permanecen `null`. `unknown` contiene sólo `null`. Esta distinción es un invariante de contrato, no inferencia estadística. `partition_id` y `source_id` son declaraciones del productor; ni hash ni etiqueta prueban disjunción o identidad."""),
    code("""state = DynamicMoments()
for x in [1., 2., 3.]: state.push(x)
wire = export_state(state)
unknown = create_envelope(wire, source_id='synthetic-fixture', partition_id='chunk-A', diagnostic_state='unknown')
tracked_zero = create_envelope(wire, source_id='synthetic-fixture', partition_id='chunk-A', diagnostic_state='tracked', diagnostic_counts={'rounded_to_zero':0,'normalization_failures':0,'rebase_events':0})
assert loads_envelope(dumps_envelope(unknown))['diagnostics']['counts']['rounded_to_zero'] is None
assert loads_envelope(dumps_envelope(tracked_zero))['diagnostics']['counts']['rounded_to_zero'] == 0
print('Wire original:', wire)
print('Unknown:', unknown['diagnostics'])
print('Tracked zero:', tracked_zero['diagnostics'])"""),
    md("""## Hashes y propiedades que no se conservan

`h_p=SHA256(ASCII(payload))`; `h_e=SHA256(JSONlocal(document sin h_e))`. El módulo ordena claves JSON y compacta separadores bajo Python. RFC 8785 especifica JCS para canonicalización interoperable; este prototipo no la implementa. Los hashes detectan cambios accidentales según bytes codificados, no autentican: un editor puede recalcularlos. No se afirma firma, seguridad frente a adversario con escritura, ni identidad de fuente."""),
    code("""tampered = dict(unknown)
tampered['provenance'] = dict(unknown['provenance'])
tampered['provenance']['partition_id'] = 'changed'
try:
    from src.audit_envelope import verify_envelope
    verify_envelope(tampered)
except ValueError as exc:
    print('Metadata mutada rechazada:', exc)
else:
    raise AssertionError('Metadata mutation passed')
summary = json.loads(Path('results/envelope_summary.json').read_text())
assert summary['all_payload_roundtrips_exact'] and summary['all_metadata_states_preserved']
summary"""),
    md("""## Comparación, ablaciones y resultados

Ambos métodos guardan los mismos campos; el sidecar plano es un baseline competitivo, no un strawman. Se reportan tamaño UTF-8 y tiempos locales, que pueden favorecer cualquiera. Ablación V1 solo no conserva status; quitar el digest del envelope no detecta metadata alterada; reemplazar `null` por cero destruye distinción. Los casos son sintéticos y no demuestran que una implementación de ingestión real reporte correctamente sus contadores."""),
    code("""print(json.dumps(summary, indent=2))
display(Image(filename='results/envelope_audit.png'))"""),
    md("""## Fallos, conclusión y siguiente experimento

Sin JCS, el JSON no tiene contrato byte-a-byte entre lenguajes; sin firma no hay autenticidad; etiquetas no demuestran particiones disjuntas; los diagnósticos no se miden ni se recolectan aquí. El resultado positivo se limita a la distinción de disponibilidad en el productor Python y detección de cambios bajo el digest local. Conclusión: H1/H2 tienen pruebas locales; la utilidad depende de una futura instrumentación. El siguiente gate es un consumidor externo JCS sólo si aparece una necesidad real de interoperar, o preservar `unknown` ante un productor que omite historial. Fuentes verificadas y sus diferencias: `prior_art_envelope.md` y `referencias.bib`."""),
]

InteractiveShell.clear_instance()
shell = InteractiveShell.instance()
for count, cell in enumerate((c for c in nb.cells if c.cell_type == "code"), start=1):
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(str(result.error_before_exec or result.error_in_exec))
    cell.execution_count = count
    cell.outputs = []
    for name, value in (("stdout", captured.stdout), ("stderr", captured.stderr)):
        if value:
            cell.outputs.append(nbf.v4.new_output("stream", name=name, text=value))
    for output in captured.outputs:
        cell.outputs.append(nbf.v4.new_output("display_data", data=output.data, metadata=output.metadata))
nbf.validate(nb)
nbf.write(nb, root / "notebook_envelope.ipynb")
