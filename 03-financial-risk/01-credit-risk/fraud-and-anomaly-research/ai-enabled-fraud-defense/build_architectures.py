"""Generate editable mxGraph pages and exact SVG views from one geometry model.

Run from any directory with Python 3.11+. No network, draw.io or external package.
SVG is our renderer, not an export certified by the draw.io application.
"""

import hashlib
import json
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
COLORS = {
    "internal": ("#eaf3fc", "#3274a5"),
    "external": ("#f2edfc", "#8061ad"),
    "review": ("#fff4d9", "#bd8730"),
}
PAGES = [
    (
        "01-kyc",
        "A · Originación y KYC ante fraude con IA",
        "Captura, autenticidad y vínculo de identidad se evalúan por separado.",
        [
            (
                "01 · Entrada",
                [
                    ("Solicitud y consentimiento", "Caso, canal y corte", "internal"),
                    ("SDK de captura", "Sesión y referencia de evidencia", "external"),
                    ("Canal alternativo", "Accesibilidad y excepciones", "review"),
                ],
            ),
            (
                "02 · Captura",
                [
                    (
                        "Documento y presencia",
                        "Original, calidad y autenticidad",
                        "external",
                    ),
                    ("Vida y rostro", "Presentación y comparación facial", "external"),
                    (
                        "Integridad de sesión",
                        "Inyección, replay y dispositivo",
                        "internal",
                    ),
                ],
            ),
            (
                "03 · Evidencia",
                [
                    (
                        "Vínculo entre fuentes",
                        "Titular, documento e identidad",
                        "internal",
                    ),
                    ("Medios manipulados", "Señal por familia y versión", "external"),
                    (
                        "Cobertura y contradicción",
                        "Estado explícito por control",
                        "internal",
                    ),
                ],
            ),
            (
                "04 · Decisión",
                [
                    (
                        "Integración y calibración",
                        "Predicciones temporales; sin sumar scores",
                        "internal",
                    ),
                    (
                        "Adaptadores de proveedor",
                        "iProov / Truora / SEON / Socure",
                        "external",
                    ),
                    (
                        "Política económica",
                        "Costo, capacidad y modo degradado",
                        "internal",
                    ),
                ],
            ),
            (
                "05 · Resolución",
                [
                    (
                        "Ruta de crédito separada",
                        "PD, LGD y EAD tienen otro objetivo",
                        "internal",
                    ),
                    (
                        "Adjudicación humana",
                        "Solicitar evidencia o resolver caso",
                        "review",
                    ),
                    (
                        "Ledger de decisión",
                        "Razones, versiones y etiquetas",
                        "internal",
                    ),
                ],
            ),
        ],
        [
            (0, 3),
            (1, 4),
            (1, 5),
            (2, 5),
            (3, 6),
            (4, 7),
            (5, 8),
            (6, 9),
            (7, 9),
            (8, 11),
            (10, 9),
            (9, 11),
            (11, 12),
            (11, 13),
            (12, 14),
            (13, 14),
        ],
    ),
    (
        "02-documents",
        "B · Documentos e ingresos con evidencia",
        "El documento aporta datos; la política y los permisos viven fuera del documento.",
        [
            (
                "01 · Ingesta",
                [
                    (
                        "Zona de archivos aislada",
                        "Tipo, tamaño y análisis de archivo",
                        "internal",
                    ),
                    (
                        "Fuente financiera conectada",
                        "Belvo como candidato; cobertura por país",
                        "external",
                    ),
                    (
                        "Permiso y trazabilidad",
                        "Titular, finalidad y disponibilidad",
                        "internal",
                    ),
                ],
            ),
            (
                "02 · Extracción",
                [
                    (
                        "Original y hash",
                        "Bytes preservados; acceso restringido",
                        "internal",
                    ),
                    ("OCR y extracción tipada", "Página, span y confianza", "internal"),
                    (
                        "Aislamiento del modelo",
                        "Sin permisos de aprobación o pago",
                        "internal",
                    ),
                ],
            ),
            (
                "03 · Contraste",
                [
                    (
                        "Soporte semántico",
                        "Salario, préstamo o transferencia",
                        "internal",
                    ),
                    (
                        "Conciliación independiente",
                        "Titular, período, moneda y flujos",
                        "internal",
                    ),
                    ("Abstención explícita", "Falta de fuente o ambigüedad", "review"),
                ],
            ),
            (
                "04 · Riesgo",
                [
                    (
                        "Discrepancia e irregularidad",
                        "Residuo robusto y cuantiles",
                        "internal",
                    ),
                    (
                        "Verificación de inconsistencia",
                        "Nueva fuente o revisión dirigida",
                        "review",
                    ),
                    ("Capacidad de pago", "Evaluación crediticia separada", "internal"),
                ],
            ),
            (
                "05 · Evidencia",
                [
                    ("Caso adjudicado", "Contradicción no equivale a fraude", "review"),
                    (
                        "Paquete de evidencia",
                        "Origen y límites de cada afirmación",
                        "internal",
                    ),
                    (
                        "Ledger y aprendizaje",
                        "Etiqueta madura; no autoetiquetar",
                        "internal",
                    ),
                ],
            ),
        ],
        [
            (0, 3),
            (3, 4),
            (2, 5),
            (4, 6),
            (1, 7),
            (6, 7),
            (5, 8),
            (4, 8),
            (7, 9),
            (8, 10),
            (7, 11),
            (9, 10),
            (10, 12),
            (11, 13),
            (12, 14),
            (13, 14),
        ],
    ),
    (
        "03-session",
        "C · Sesión, coerción y desembolso",
        "KYC inicial y autenticación correcta no resuelven todos los riesgos de intención.",
        [
            (
                "01 · Contexto",
                [
                    (
                        "Autenticación y sesión",
                        "Evento, dispositivo y cambios",
                        "internal",
                    ),
                    (
                        "Señales conductuales",
                        "BioCatch / Feedzai como candidatos",
                        "external",
                    ),
                    ("Destino de fondos", "Titular y beneficiario nuevo", "internal"),
                ],
            ),
            (
                "02 · Detección",
                [
                    ("Toma de cuenta", "Modelo temporal y reglas", "internal"),
                    (
                        "Coerción o estafa",
                        "Contexto y señales; intención incierta",
                        "internal",
                    ),
                    (
                        "Cambios de alto impacto",
                        "Destino, credenciales y dispositivo",
                        "internal",
                    ),
                ],
            ),
            (
                "03 · Política",
                [
                    (
                        "Estado de evidencia",
                        "Vigencia, cobertura y contradicción",
                        "internal",
                    ),
                    ("Costo y capacidad", "Continuar, verificar o retener", "internal"),
                    ("Modo degradado", "Timeout y cola con plazo", "review"),
                ],
            ),
            (
                "04 · Acción",
                [
                    ("Verificación adicional", "Canal previamente confiable", "review"),
                    (
                        "Autorización de pagos",
                        "Check final de destino y vigencia",
                        "internal",
                    ),
                    (
                        "Revisión especializada",
                        "Coerción, ATO o evidencia insuficiente",
                        "review",
                    ),
                ],
            ),
            (
                "05 · Efecto",
                [
                    (
                        "Ejecución idempotente",
                        "Clave única y transacción durable",
                        "internal",
                    ),
                    (
                        "Ledger de efecto",
                        "Decision_id enlazado a effect_id",
                        "internal",
                    ),
                    (
                        "Seguimiento y resolución",
                        "Pérdida madura y apelación",
                        "review",
                    ),
                ],
            ),
        ],
        [
            (0, 3),
            (1, 4),
            (2, 5),
            (3, 6),
            (4, 6),
            (5, 6),
            (6, 7),
            (6, 8),
            (7, 9),
            (7, 10),
            (8, 11),
            (9, 10),
            (10, 12),
            (11, 14),
            (12, 13),
            (13, 14),
        ],
    ),
    (
        "04-network",
        "D · Redes, etiquetas y vigilancia de modelos",
        "El monitoreo abre investigación; una alerta no se convierte automáticamente en etiqueta.",
        [
            (
                "01 · Registro",
                [
                    (
                        "Eventos bitemporales",
                        "Fecha del hecho y de disponibilidad",
                        "internal",
                    ),
                    (
                        "Señales de proveedores",
                        "Versión, cobertura y cambios",
                        "external",
                    ),
                    (
                        "Adjudicación y muestreo",
                        "Aprobados y alertados; label madura",
                        "review",
                    ),
                ],
            ),
            (
                "02 · Snapshot",
                [
                    ("Grafo al corte", "Relaciones tipadas y caducidad", "internal"),
                    (
                        "Variables por canal",
                        "Mezcla, exposición y denominador",
                        "internal",
                    ),
                    (
                        "Catálogo de etiquetas",
                        "Fraude, default, ATO y desconocido",
                        "internal",
                    ),
                ],
            ),
            (
                "03 · Modelos",
                [
                    (
                        "Conteos y GNN challenger",
                        "Camuflaje y vecinos benignos",
                        "internal",
                    ),
                    (
                        "Drift y calibración",
                        "Alertas múltiples y retraso de label",
                        "internal",
                    ),
                    (
                        "Validación temporal",
                        "Agrupar identidad y componente",
                        "internal",
                    ),
                ],
            ),
            (
                "04 · Diagnóstico",
                [
                    (
                        "Investigación de red",
                        "Prioridad por caso y deduplicación",
                        "review",
                    ),
                    (
                        "Diagnóstico de cambio",
                        "Proveedor, población o modelo",
                        "review",
                    ),
                    ("Registro de modelos", "Política congelada y replay", "internal"),
                ],
            ),
            (
                "05 · Liberación",
                [
                    (
                        "Caso y ledger de pérdida",
                        "Atribución sin doble conteo",
                        "internal",
                    ),
                    (
                        "Sombra y aprobación",
                        "Métricas y responsables definidos",
                        "review",
                    ),
                    (
                        "Nueva versión o rollback",
                        "Sin reentrenar con alerta = fraude",
                        "internal",
                    ),
                ],
            ),
        ],
        [
            (0, 3),
            (1, 4),
            (2, 5),
            (3, 6),
            (4, 7),
            (5, 8),
            (6, 8),
            (6, 9),
            (7, 10),
            (8, 11),
            (9, 12),
            (10, 13),
            (11, 13),
            (13, 14),
        ],
    ),
]


def geometry(rows):
    result = []
    for ri, (_, nodes) in enumerate(rows):
        for ci, (title, detail, kind) in enumerate(nodes):
            result.append(
                {
                    "id": f"n{len(result)}",
                    "x": 205 + 430 * ci,
                    "y": 211 + 170 * ri,
                    "w": 390,
                    "h": 94,
                    "title": title,
                    "detail": detail,
                    "kind": kind,
                }
            )
    return result


def edge_path(a, b):
    # Adjacent boxes in a row use horizontal ports. Otherwise route via row gutters.
    if a["y"] == b["y"]:
        if abs(a["x"] - b["x"]) > 430:
            y = a["y"] + a["h"]
            return [
                (a["x"] + 195, y),
                (a["x"] + 195, y + 16),
                (b["x"] + 195, y + 16),
                (b["x"] + 195, y),
            ]
        if a["x"] < b["x"]:
            return [(a["x"] + a["w"], a["y"] + 47), (b["x"], b["y"] + 47)]
        return [(a["x"], a["y"] + 47), (b["x"] + b["w"], b["y"] + 47)]
    start = (a["x"] + 195, a["y"] + 94)
    end = (b["x"] + 195, b["y"])
    if b["y"] - a["y"] > 170:
        return [
            start,
            (start[0], start[1] + 16),
            (1490, start[1] + 16),
            (1490, end[1] - 16),
            (end[0], end[1] - 16),
            end,
        ]
    mid = (start[1] + end[1]) / 2
    return [start, (start[0], mid), (end[0], mid), end]


def wrap(text, limit=39):
    lines = [""]
    for word in text.split():
        if len(lines[-1]) + len(word) + 1 > limit:
            lines.append(word)
        else:
            lines[-1] = (lines[-1] + " " + word).strip()
    return lines


def generate():
    dest = ROOT / "diagrams"
    dest.mkdir(exist_ok=True)
    mxfile = ET.Element(
        "mxfile", host="app.diagrams.net", version="24.7.17", type="device"
    )
    manifest = []
    for slug, title, subtitle, rows, edges in PAGES:
        nodes = geometry(rows)
        page = ET.SubElement(mxfile, "diagram", id=slug, name=title)
        model = ET.SubElement(
            page,
            "mxGraphModel",
            dx="1540",
            dy="1130",
            grid="1",
            gridSize="10",
            page="1",
            pageWidth="1540",
            pageHeight="1130",
            pageScale="1",
        )
        root = ET.SubElement(model, "root")
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")

        def cell(cid, value, style, x, y, w, h, root=root):
            el = ET.SubElement(
                root, "mxCell", id=cid, value=value, style=style, vertex="1", parent="1"
            )
            ET.SubElement(
                el,
                "mxGeometry",
                x=str(x),
                y=str(y),
                width=str(w),
                height=str(h),
                attrib={"as": "geometry"},
            )

        cell(
            "title",
            title,
            "text;html=0;fontSize=28;fontStyle=1;align=left;",
            38,
            26,
            1460,
            48,
        )
        cell(
            "subtitle",
            subtitle,
            "text;html=0;fontSize=16;align=left;",
            38,
            82,
            1460,
            40,
        )
        cell(
            "legend",
            "DISEÑO S1 · Azul: interno | Violeta: proveedor candidato | Ámbar: revisión/estado",
            "text;html=0;fontSize=14;align=left;",
            38,
            132,
            1460,
            32,
        )
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="1540" height="1130" viewBox="0 0 1540 1130"><title>{escape(title)}</title><desc>Arquitectura de investigación por capas; integraciones no desplegadas.</desc><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#42596d"/></marker></defs><rect width="1540" height="1130" fill="#ffffff"/><g font-family="DejaVu Sans,Arial,sans-serif" fill="#17334d">',
            f'<text x="38" y="60" font-size="28" font-weight="bold">{escape(title)}</text>',
            f'<text x="38" y="102" font-size="17">{escape(subtitle)}</text>',
            '<text x="38" y="148" font-size="14">DISEÑO S1 · Azul: interno | Violeta: proveedor candidato | Ámbar: revisión/estado</text>',
        ]
        for i, (label, _) in enumerate(rows):
            y = 180 + i * 170
            cell(
                f"layer{i}",
                label,
                "rounded=1;fillColor=#f7f9fc;strokeColor=#d9e2ec;align=left;verticalAlign=top;spacingLeft=15;spacingTop=18;fontSize=16;fontStyle=1;",
                25,
                y,
                1490,
                150,
            )
            svg.append(
                f'<rect x="25" y="{y}" width="1490" height="150" rx="10" fill="#f7f9fc" stroke="#d9e2ec"/>'
            )
            for j, line in enumerate(wrap(label, 12)):
                svg.append(
                    f'<text x="42" y="{y + 43 + j * 24}" font-size="17" font-weight="bold">{escape(line)}</text>'
                )
        # Edges are independent editable mxGraph cells with explicit shared SVG waypoints.
        for i, (a, b) in enumerate(edges):
            points = edge_path(nodes[a], nodes[b])
            same = nodes[a]["y"] == nodes[b]["y"]
            right = nodes[a]["x"] < nodes[b]["x"]
            long_same = same and abs(nodes[a]["x"] - nodes[b]["x"]) > 430
            ports = (
                (
                    "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
                    if right
                    else "exitX=0;exitY=0.5;entryX=1;entryY=0.5;"
                )
                if same
                else "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"
            )
            if long_same:
                ports = "exitX=0.5;exitY=1;entryX=0.5;entryY=1;"
            el = ET.SubElement(
                root,
                "mxCell",
                id=f"e{i}",
                edge="1",
                parent="1",
                source=f"n{a}",
                target=f"n{b}",
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;strokeColor=#42596d;strokeWidth=2;"
                + ports,
            )
            geo = ET.SubElement(
                el, "mxGeometry", relative="1", attrib={"as": "geometry"}
            )
            if len(points) > 2:
                arr = ET.SubElement(geo, "Array", attrib={"as": "points"})
                for x, y in points[1:-1]:
                    ET.SubElement(arr, "mxPoint", x=str(x), y=str(y))
            coords = " ".join(f"{x},{y}" for x, y in points)
            svg.append(
                f'<polyline points="{coords}" fill="none" stroke="#42596d" stroke-width="2" marker-end="url(#arrow)"/>'
            )
        for n in nodes:
            fill, stroke = COLORS[n["kind"]]
            value = n["title"] + "\n" + n["detail"]
            cell(
                n["id"],
                value,
                f"rounded=1;whiteSpace=wrap;html=0;fillColor={fill};strokeColor={stroke};fontColor=#17334d;fontSize=16;spacing=9;",
                n["x"],
                n["y"],
                n["w"],
                n["h"],
            )
            svg.append(
                f'<rect x="{n["x"]}" y="{n["y"]}" width="390" height="94" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="1.7"/>'
            )
            svg.append(
                f'<text x="{n["x"] + 16}" y="{n["y"] + 29}" font-size="17" font-weight="bold">{escape(n["title"])}</text>'
            )
            for j, line in enumerate(wrap(n["detail"])):
                svg.append(
                    f'<text x="{n["x"] + 16}" y="{n["y"] + 54 + j * 20}" font-size="15">{escape(line)}</text>'
                )
        footer = "Transversal: acceso mínimo · privacidad · auditoría · versiones · retención · responsables · rollback"
        cell(
            "footer", footer, "text;html=0;fontSize=15;align=left;", 38, 1045, 1460, 35
        )
        svg.append(f'<text x="38" y="1072" font-size="16">{escape(footer)}</text>')
        svg.append(
            '<text x="38" y="1104" font-size="13">Portafolio · 23 octubre 2026 · Flechas: datos/decisiones propuestos · Véase ARCHITECTURES.md para alcance y fallos</text></g></svg>'
        )
        target = dest / (slug + ".svg")
        target.write_text("\n".join(svg) + "\n")
        manifest.append(
            {
                "page": slug,
                "nodes": len(nodes),
                "edges": len(edges),
                "svg_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            }
        )
    path = dest / "fraud-defense.drawio"
    ET.indent(mxfile)
    ET.ElementTree(mxfile).write(path, encoding="utf-8", xml_declaration=True)
    # Validate native editability: nodes, geometries and actual edge references, not embedded screenshots.
    for page in mxfile.findall("diagram"):
        cells = page.findall(".//mxCell")
        ids = {c.get("id") for c in cells}
        assert len(ids) == len(cells)
        for c in cells:
            if c.get("edge") == "1":
                assert c.get("source") in ids and c.get("target") in ids
            if c.get("vertex") == "1":
                assert c.find("mxGeometry") is not None
    for entry in manifest:
        ET.parse(dest / (entry["page"] + ".svg"))
    (dest / "manifest.json").write_text(
        json.dumps(
            {
                "renderer": "Shared geometry; native uncompressed mxGraph XML + custom SVG. draw.io GUI round-trip not performed.",
                "drawio_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "pages": manifest,
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(manifest))


if __name__ == "__main__":
    generate()
