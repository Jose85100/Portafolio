#!/usr/bin/env python3
"""Rank IDEAM rain-station catalog entries near illustrative city centroids.

This is station discovery only. It does not fetch station observations, validate
instrument histories, or establish suitability for any insured property.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


# Approximate urban reference points, used only to find candidate stations.
CITY_COORDS = {
    "Barrancabermeja": (7.0653, -73.8547), "Barranquilla": (10.9639, -74.7964),
    "Bogotá": (4.7110, -74.0721), "Bucaramanga": (7.1193, -73.1227),
    "Cali": (3.4516, -76.5320), "Cartagena": (10.3910, -75.4794),
    "Medellín": (6.2442, -75.5812), "Neiva": (2.9273, -75.2819),
    "Pasto": (1.2136, -77.2811), "Villavicencio": (4.1420, -73.6266),
}
RAIN_TYPES = {"Pluviométrica", "Pluviográfica", "Climatológica Ordinaria",
              "Climatológica Principal", "Agrometeorológica"}


def haversine_km(lat1: float, lon1: float, lat2: pd.Series, lon2: pd.Series) -> pd.Series:
    from numpy import arcsin, cos, radians, sin, sqrt
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 6371.0088 * 2 * arcsin(sqrt(a))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=Path(__file__).parent / "data" / "ideam_station_catalog_2026-11-11.csv")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "results")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw = args.catalog.read_bytes()
    catalog = pd.read_csv(args.catalog, dtype=str)
    required = {"codigo", "nombre", "categoria", "tecnologia", "estado", "departamento", "municipio", "altitud", "longitud", "latitud", "fecha_instalacion", "fecha_suspension", "entidad"}
    missing = sorted(required - set(catalog.columns))
    if missing:
        raise ValueError(f"Catalog fields missing: {missing}")
    downloaded_rows = len(catalog)
    duplicate_full_rows = int(catalog.duplicated().sum())
    catalog = catalog.drop_duplicates().copy()
    duplicate_station_codes = int(catalog.codigo.duplicated().sum())
    catalog["latitud_num"] = pd.to_numeric(catalog.latitud, errors="coerce")
    catalog["longitud_num"] = pd.to_numeric(catalog.longitud, errors="coerce")
    candidates = catalog.loc[catalog.categoria.isin(RAIN_TYPES)].copy()
    candidates["catalog_status_active"] = candidates.estado.str.casefold().eq("activa")
    candidates["latlon_valid"] = candidates.latitud_num.between(-5, 14) & candidates.longitud_num.between(-82, -66)
    candidates = candidates.loc[candidates.latlon_valid].copy()

    rows = []
    for city, (lat, lon) in CITY_COORDS.items():
        ranked = candidates.copy()
        ranked["distance_km"] = haversine_km(lat, lon, ranked.latitud_num, ranked.longitud_num)
        ranked = ranked.sort_values(["distance_km", "codigo"]).head(5)
        for rank, (_, station) in enumerate(ranked.iterrows(), start=1):
            rows.append({"city_reference": city, "city_latitude": lat, "city_longitude": lon,
                         "rank": rank, "distance_km": round(float(station.distance_km), 3),
                         "codigo": station.codigo, "nombre": station.nombre,
                         "categoria": station.categoria, "tecnologia": station.tecnologia,
                         "estado_catalogo": station.estado, "departamento": station.departamento,
                         "municipio": station.municipio, "altitud_m": station.altitud,
                         "station_latitude": station.latitud, "station_longitude": station.longitud,
                         "fecha_instalacion": station.fecha_instalacion,
                         "fecha_suspension": station.fecha_suspension, "entidad": station.entidad})
    output = pd.DataFrame(rows)
    output.to_csv(args.output_dir / "nearest_candidate_stations.csv", index=False)
    manifest = {
        "source": "IDEAM Catálogo Nacional de Estaciones, datos abiertos resource hp9r-jxuu",
        "source_url": "https://www.datos.gov.co/d/hp9r-jxuu",
        "catalog_snapshot_date": "2026-11-11",
        "catalog_file": args.catalog.name,
        "catalog_sha256": hashlib.sha256(raw).hexdigest(),
        "rows_downloaded": downloaded_rows,
        "rows_after_exact_duplicate_removal": len(catalog),
        "duplicate_full_rows_removed": duplicate_full_rows,
        "duplicate_station_codes_remaining": duplicate_station_codes,
        "catalog_page_reported_rows": 9685,
        "api_limit_requested": 10000,
        "candidate_rain_categories": sorted(RAIN_TYPES),
        "candidate_rows_with_valid_colombia_coordinates": len(candidates),
        "city_centroids": {k: {"latitude": v[0], "longitude": v[1]} for k, v in CITY_COORDS.items()},
        "interpretation": "Catalog-only proximity screening. No station time series, approval/quality flags, data completeness, property coordinates, exposure, damage, or payout data were obtained.",
        "limits": ["nearest station to city centroid is not necessarily nearest to an insured site",
                   "distance does not establish terrain or hydrological representativeness",
                   "catalog operational status does not prove period-specific observations exist",
                   "download was capped at 10000 rows; confirm completeness against current catalog before relying on ranks"],
    }
    (args.output_dir / "catalog_quality_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"rows_downloaded": downloaded_rows, "duplicate_full_rows_removed": duplicate_full_rows,
                      "duplicate_station_codes_remaining": duplicate_station_codes,
                      "rain_candidates_with_coordinates": len(candidates),
                      "nearest_candidates": output.groupby("city_reference", sort=False).first().reset_index()[["city_reference", "codigo", "nombre", "distance_km", "estado_catalogo"]].to_dict(orient="records")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
