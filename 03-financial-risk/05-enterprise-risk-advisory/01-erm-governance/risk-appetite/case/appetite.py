"""Illustrative risk-appetite dashboard with explicit scenario observations.

Inputs and thresholds are illustrative, not approved limits or regulatory rules.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def number(value, field):
    if isinstance(value, bool):
        raise ValueError(f"{field}: expected a finite number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field}: expected a finite number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{field}: expected a finite number")
    return result


def evaluate(config, observations):
    """Return one row per configured scenario/metric, including missing values."""
    scenarios = config.get("scenarios")
    metrics = config.get("metrics")
    if not isinstance(scenarios, list) or not scenarios or any(not isinstance(s, str) or not s.strip() for s in scenarios) or len(set(scenarios)) != len(scenarios):
        raise ValueError("scenarios must be a nonempty list of unique names")
    if not isinstance(metrics, list) or not metrics:
        raise ValueError("metrics must be a nonempty list")
    definitions = {}
    for metric in metrics:
        for field in ("id", "label", "unit", "direction", "owner", "action"):
            if not isinstance(metric.get(field), str) or not metric[field].strip():
                raise ValueError(f"invalid metric field {field}")
        key = metric["id"]
        if key in definitions:
            raise ValueError(f"duplicate metric {key}")
        warning = number(metric.get("warning"), f"{key}.warning")
        limit = number(metric.get("limit"), f"{key}.limit")
        minimum = number(metric.get("minimum"), f"{key}.minimum")
        maximum = number(metric.get("maximum"), f"{key}.maximum")
        if minimum >= maximum or not (minimum <= warning <= maximum and minimum <= limit <= maximum):
            raise ValueError(f"{key}: invalid bounds or thresholds")
        direction = metric["direction"]
        if direction not in ("upper", "lower"):
            raise ValueError(f"{key}: invalid direction")
        if (direction == "upper" and warning >= limit) or (direction == "lower" and warning <= limit):
            raise ValueError(f"{key}: warning must precede limit")
        definitions[key] = (metric, warning, limit, minimum, maximum)

    values = {}
    for row in observations:
        scenario, key = row.get("scenario"), row.get("metric_id")
        if scenario not in scenarios or key not in definitions:
            raise ValueError(f"unknown scenario/metric: {scenario}/{key}")
        if (scenario, key) in values:
            raise ValueError(f"duplicate observation: {scenario}/{key}")
        if row.get("unit") != definitions[key][0]["unit"]:
            raise ValueError(f"{scenario}/{key}: unit mismatch")
        value = number(row.get("value"), f"{scenario}/{key}.value")
        if not definitions[key][3] <= value <= definitions[key][4]:
            raise ValueError(f"{scenario}/{key}: outside configured bounds")
        values[scenario, key] = value

    output = []
    for scenario in scenarios:
        for key, (metric, warning, limit, _minimum, _maximum) in definitions.items():
            value = values.get((scenario, key))
            if value is None:
                status = "SIN DATO"
            elif (value >= limit if metric["direction"] == "upper" else value <= limit):
                status = "BRECHA"
            elif (value >= warning if metric["direction"] == "upper" else value <= warning):
                status = "ALERTA"
            else:
                status = "NORMAL"
            action = "Mantener seguimiento" if status == "NORMAL" else ("Obtener o corregir dato" if status == "SIN DATO" else metric["action"])
            output.append({"scenario": scenario, "metric_id": key, "label": metric["label"],
                           "unit": metric["unit"], "value": value, "warning": warning,
                           "limit": limit, "direction": metric["direction"], "status": status,
                           "owner": metric["owner"], "action": action})
    return output


def report(rows):
    lines = ["# Comité de riesgos — ejercicio sintético", "",
             "Umbrales, datos y acciones son ilustrativos; no son límites aprobados.", "",
             "| Escenario | Indicador | Valor | Alerta | Límite | Estado | Responsable | Acción sugerida |",
             "|---|---|---:|---:|---:|---|---|---|"]
    for row in rows:
        value = "—" if row["value"] is None else f"{row['value']:g} {row['unit']}"
        lines.append(f"| {row['scenario']} | {row['label']} | {value} | {row['warning']:g} | {row['limit']:g} | {row['status']} | {row['owner']} | {row['action']} |")
    lines.extend(["", "Los límites y alertas están expresados en la unidad del indicador. "
                  "SIN DATO exige obtener o corregir la observación antes de decidir; "
                  "no implica cumplimiento. Las acciones requieren revisión humana.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    parser.add_argument("--observations", type=Path, default=Path(__file__).with_name("observations.csv"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    with args.observations.open(encoding="utf-8", newline="") as source:
        observations = list(csv.DictReader(source))
    print(report(evaluate(config, observations)), end="")


if __name__ == "__main__":
    main()
