#!/usr/bin/env python3
"""
Reduccion H3: H*_skill, H*_evento, H*_fidelidad por (estacion, modelo).

No reentrena nada. Reduce resultados ya calculados y congelados en
fedeg-umh-es/varret-pm10-paper (commit 4a49b08b041c578ec5981dc1472125b2af0a4d59),
fichero outputs/tables/master_diagnostic_table.csv (595 filas = 17 estaciones
x 7 horizontes x 5 modelos).

REGLA DE ESTE SCRIPT: las tres definiciones se toman LITERALMENTE del codigo
congelado. No se construye ningun criterio nuevo, no se combina una metrica
con un baseline que el codigo no combine, y no se introduce ninguna regla de
exclusion que el artefacto no declare.

Definiciones (todas preexistentes, con su procedencia exacta):

  Regla de reduccion comun -- "strict" / primer cruce:
      p32_ijf_ghostskill_hstar/src/diagnostics/hstar.py::compute_hstar
      criterion="strict": recorre h=1,2,... y se detiene al primer fallo;
      devuelve el ultimo horizonte consecutivo que cumple la condicion.
      Se aplica identica a las tres dimensiones.

  H*_skill      condicion: skill > 0
                skill = 1 - RMSE_modelo/RMSE_persistence, columna "skill"
                de master_diagnostic_table.csv, construida por
                hstar.py::build_skill_table (baseline = persistence).

  H*_fidelidad  condicion: alpha >= 0.50
                alpha = Var(pred)/Var(true), ddof=0 (NO SD/SD; confirmado en
                varret-pm10-paper/audit/paper_a_alpha_var_sd/report.md).
                Umbral 0.50 = collapse_threshold en
                p32/src/diagnostics/variance.py::detect_variance_collapse,
                identico a ALPHA_PRIMARY en
                varret-pm10-paper/scripts/15_decision_change_analysis.py.

  H*_evento     condicion: recall_p75 >= 0.20
                Unico criterio de evento congelado del proyecto:
                RECALL_PRIMARY = 0.20 sobre recall_p75, en
                scripts/15_decision_change_analysis.py (Rule B) y replicado
                en audit/decision_change/verify_decision_change.py.
                recall_p75 = recall de superacion del percentil 75 movil del
                historico previo al origen (scripts/03_exceedance_analysis.py).

SOPORTE COMUN (declarado, no corregido aqui):
  master_diagnostic_table.csv trae la columna "n" (tamano muestral por celda).
  Los modelos hgb_direct, ridge_direct, seasonal_naive y stl_ridge_direct
  comparten n exactamente dentro de cada (dataset, horizonte): n ~ 1118-1731.
  sarima NO: n ~ 127-180, un orden de magnitud menor, porque se genero con
  origenes cada 14 dias (scripts/02_generate_sarima_predictions.py
  --origin-step 14) mientras el resto usa origenes diarios. Por tanto las
  filas de sarima NO son comparables celda a celda con las demas. Se emiten,
  pero marcadas common_support=False, y deben excluirse de cualquier
  comparacion entre modelos.

  El artefacto congelado declara low_sample_flag=False en las 595 celdas: no
  hay ninguna celda de bajo soporte segun el propio proyecto. Este script NO
  anade ninguna regla de exclusion adicional por recuento de eventos.

Salida: outputs/h3_table.csv + outputs/h3_run_metadata.json.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
EVID = ROOT / "evidence" / "varret-pm10-paper_4a49b08"
MASTER = EVID / "master_diagnostic_table.csv"
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(exist_ok=True)

SOURCE_REPO = "fedeg-umh-es/varret-pm10-paper"
SOURCE_COMMIT = "4a49b08b041c578ec5981dc1472125b2af0a4d59"

ALPHA_THRESH = 0.50   # variance.py collapse_threshold == script 15 ALPHA_PRIMARY
RECALL_THRESH = 0.20  # script 15 RECALL_PRIMARY
HORIZONS = list(range(1, 8))
NON_COMMON_SUPPORT_MODELS = {"sarima"}  # origin-step 14, n ~10x menor


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hstar_strict(values_by_h: dict[int, float], predicate) -> int:
    """hstar.py::compute_hstar(criterion='strict'): ultimo horizonte
    consecutivo desde h=1 que cumple predicate; se detiene al primer fallo."""
    hstar = 0
    for h in HORIZONS:
        v = values_by_h.get(h)
        if v is None or pd.isna(v) or not predicate(v):
            break
        hstar = h
    return hstar


def main() -> None:
    master = pd.read_csv(MASTER)

    rows = []
    for (dataset, model), g in master.groupby(["dataset", "model"], sort=True):
        g = g.set_index("horizon")
        meta = g.iloc[0]

        h_skill = hstar_strict(g["skill"].to_dict(), lambda v: v > 0)
        h_fidelidad = hstar_strict(g["alpha"].to_dict(), lambda v: v >= ALPHA_THRESH)
        h_evento = hstar_strict(g["recall_p75"].to_dict(), lambda v: v >= RECALL_THRESH)

        rows.append(
            {
                "dataset": dataset,
                "station_id": meta.get("station_id"),
                "station_name": meta.get("station_name"),
                "province": meta.get("province"),
                "station_type": meta.get("station_type"),
                "model": model,
                "H_star_skill": h_skill,
                "H_star_evento": h_evento,
                "H_star_fidelidad": h_fidelidad,
                "H_star_skill_censored": h_skill == 7,
                "H_star_evento_censored": h_evento == 7,
                "H_star_fidelidad_censored": h_fidelidad == 7,
                "common_support": model not in NON_COMMON_SUPPORT_MODELS,
                "n_min": int(g["n"].min()),
                "n_max": int(g["n"].max()),
                "low_sample_flag_any": bool(g["low_sample_flag"].any()),
                "n_horizons_available": int(g.index.isin(HORIZONS).sum()),
            }
        )

    out = pd.DataFrame(rows).sort_values(["dataset", "model"]).reset_index(drop=True)
    out_path = OUT_DIR / "h3_table.csv"
    out.to_csv(out_path, index=False)

    metadata = {
        "source_repo": SOURCE_REPO,
        "source_commit": SOURCE_COMMIT,
        "source_files": {"master_diagnostic_table.csv": sha256(MASTER)},
        "reduction_rule": (
            "strict / first-crossing, identical for all three dimensions: "
            "p32_ijf_ghostskill_hstar/src/diagnostics/hstar.py::compute_hstar(criterion='strict') "
            "-- last consecutive horizon from h=1 satisfying the condition, stop at first failure."
        ),
        "definitions": {
            "H_star_skill": {
                "condition": "skill > 0",
                "metric": "skill = 1 - RMSE_model/RMSE_persistence (column 'skill')",
                "provenance": "p32_ijf_ghostskill_hstar/src/diagnostics/hstar.py::build_skill_table",
            },
            "H_star_fidelidad": {
                "condition": "alpha >= 0.50",
                "metric": "alpha = Var(pred)/Var(true), ddof=0",
                "provenance": "p32/src/diagnostics/variance.py::detect_variance_collapse "
                              "(collapse_threshold=0.5) == scripts/15_decision_change_analysis.py ALPHA_PRIMARY; "
                              "Var-ratio (not SD-ratio) confirmed in audit/paper_a_alpha_var_sd/report.md",
            },
            "H_star_evento": {
                "condition": "recall_p75 >= 0.20",
                "metric": "recall_p75 = recall of exceedance over the rolling P75 of the "
                          "pre-origin history (scripts/03_exceedance_analysis.py)",
                "provenance": "scripts/15_decision_change_analysis.py RECALL_PRIMARY=0.20 (Rule B), "
                              "replicated in audit/decision_change/verify_decision_change.py. "
                              "This is the ONLY frozen event criterion in the project.",
            },
        },
        "common_support": {
            "shared_n_models": ["hgb_direct", "ridge_direct", "seasonal_naive", "stl_ridge_direct"],
            "shared_n_range": "1118-1731, identical across these models within each (dataset,horizon)",
            "excluded_from_cross_model_comparison": ["sarima"],
            "sarima_n_range": "127-180",
            "sarima_reason": "generated with --origin-step 14 (weekly-stride origins) by "
                             "scripts/02_generate_sarima_predictions.py, while all other models use "
                             "daily origins; ~10x fewer evaluation points, so its cells are not "
                             "comparable to the others. Emitted with common_support=False.",
            "low_sample_flag_in_source": "False for all 595 cells; no additional exclusion rule is "
                                          "introduced by this script.",
        },
        "script": "scripts/compute_h3_table.py",
        "script_sha256": sha256(Path(__file__)),
        "output": str(out_path.relative_to(ROOT)),
        "n_rows": len(out),
        "n_datasets": int(out["dataset"].nunique()),
        "n_models": int(out["model"].nunique()),
        "n_rows_common_support": int(out["common_support"].sum()),
    }
    (OUT_DIR / "h3_run_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False)
    )

    print(out.to_string(index=False))
    print(f"\nWrote {out_path} ({len(out)} rows; {out['common_support'].sum()} in common support)")


if __name__ == "__main__":
    main()
