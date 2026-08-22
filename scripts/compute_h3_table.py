#!/usr/bin/env python3
"""
Reduccion H3: H*_skill, H*_evento, H*_fidelidad por (estacion, modelo).

No reentrena nada. Lee dos tablas ya calculadas y congeladas en
fedeg-umh-es/varret-pm10-paper (commit 4a49b08b041c578ec5981dc1472125b2af0a4d59):

  - outputs/tables/master_diagnostic_table.csv
      595 filas = 17 estaciones x 7 horizontes x 5 modelos candidatos
      (hgb_direct, ridge_direct, sarima, seasonal_naive, stl_ridge_direct)
      columnas usadas: skill (=1 - RMSE_modelo/RMSE_persistence, definido en
      p32_ijf_ghostskill_hstar/src/diagnostics/hstar.py::build_skill_table),
      alpha (=Var(pred)/Var(true), NO SD/SD -- confirmado en
      audit/paper_a_alpha_var_sd/report.md), f1_abs_50, recall_abs_50,
      base_rate_abs_50, n.

  - outputs/tables/exceedance_all_stations.csv
      Igual rejilla pero incluye tambien las filas model=="persistence"
      (ausentes en master_diagnostic_table.csv), necesarias para construir
      el "skill de evento" = f1_modelo(abs_50) - f1_persistencia(abs_50).

Definiciones usadas, tal como estan implementadas en el codigo (no inventadas
aqui):

  H*_skill      -> src/diagnostics/hstar.py::compute_hstar(criterion="strict")
                   en fedeg-umh-es/p32_ijf_ghostskill_hstar:
                   mayor h tal que skill(j) > 0 para todo j <= h, empezando
                   en h=1 (regla de PRIMER CRUCE, no maximo global).
                   Baseline = persistence UNICAMENTE (asi esta calculada la
                   columna "skill" en master_diagnostic_table.csv). El
                   protocolo congelado pedia doble referencia
                   (persistence Y seasonal-naive); esa segunda referencia NO
                   esta materializada como columna en ninguna tabla
                   agregada del repo -- exigiria volver a las predicciones
                   row-level (predictions_all_stations.csv, no descargado,
                   sin auditoria de fuga). Se deja constancia explicita de
                   esta limitacion; no se aproxima ni se inventa.

  H*_fidelidad  -> src/diagnostics/variance.py::detect_variance_collapse,
                   collapse_threshold=0.5 (mismo valor citado en
                   scripts/15_decision_change_analysis.py como
                   ALPHA_PRIMARY). Primer cruce: mayor h tal que
                   alpha(j) >= 0.5 para todo j <= h.

  H*_evento     -> scripts/03_exceedance_analysis.py define exactamente TRES
                   umbrales: p75, p90 y abs_50 (50 ug/m3, coincide con el
                   limite diario de la Dir. 2008/50/CE). La metrica
                   implementada es F1 (recall/precision tambien
                   disponibles); CSI NO esta implementado en ningun script
                   de este repo -- se usa F1 como metrica de evento, no CSI,
                   porque inventar CSI aqui violaria la regla de "leer del
                   repo, no asumir". Se usa el umbral abs_50 por ser el unico
                   de los tres que coincide con un limite regulatorio fijo
                   (los otros son percentiles moviles del propio historico,
                   no un evento operacional fijo). H*_evento = primer cruce
                   de (F1_modelo(abs_50,j) - F1_persistence(abs_50,j)) > 0
                   para todo j <= h. Estaciones con < 20 superaciones
                   estimadas en el soporte (base_rate_abs_50 * n < 20) se
                   marcan H*_evento = NA en vez de 0, replicando la regla ya
                   congelada.

Salida: outputs/h3_table.csv (una fila por estacion x modelo) +
outputs/h3_run_metadata.json.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
EVID = ROOT / "evidence" / "varret-pm10-paper_4a49b08"
MASTER = EVID / "master_diagnostic_table.csv"
EXCEED = EVID / "exceedance_all_stations.csv"
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(exist_ok=True)

SOURCE_REPO = "fedeg-umh-es/varret-pm10-paper"
SOURCE_COMMIT = "4a49b08b041c578ec5981dc1472125b2af0a4d59"
ALPHA_THRESH = 0.5
MIN_EXCEEDANCES = 20
HORIZONS = list(range(1, 8))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def first_crossing(values_by_h: dict[int, float | None], predicate) -> int | None:
    """Mayor h tal que predicate(values_by_h[j]) es True para todo j=1..h.
    None si el valor en h=1 ya falla o falta un horizonte intermedio."""
    hstar = 0
    for h in HORIZONS:
        v = values_by_h.get(h)
        if v is None or pd.isna(v):
            break
        if predicate(v):
            hstar = h
        else:
            break
    return hstar


def main() -> None:
    master = pd.read_csv(MASTER)
    exceed = pd.read_csv(EXCEED)

    persistence_f1 = (
        exceed[(exceed["model"] == "persistence") & (exceed["threshold_type"] == "abs_50")]
        [["dataset", "horizon", "f1"]]
        .rename(columns={"f1": "f1_abs_50_persistence"})
    )

    df = master.merge(persistence_f1, on=["dataset", "horizon"], how="left")
    df["event_skill_abs_50"] = df["f1_abs_50"] - df["f1_abs_50_persistence"]
    df["n_exceedances_est"] = df["base_rate_abs_50"] * df["n"]

    rows = []
    for (dataset, model), g in df.groupby(["dataset", "model"], sort=True):
        g = g.set_index("horizon")
        meta = g.iloc[0]

        skill_by_h = g["skill"].to_dict()
        alpha_by_h = g["alpha"].to_dict()
        event_skill_by_h = g["event_skill_abs_50"].to_dict()
        n_exceed_by_h = g["n_exceedances_est"].to_dict()

        h_skill = first_crossing(skill_by_h, lambda v: v > 0)
        h_fidelidad = first_crossing(alpha_by_h, lambda v: v >= ALPHA_THRESH)

        low_support = any(
            (n_exceed_by_h.get(h) is not None and not pd.isna(n_exceed_by_h.get(h)) and n_exceed_by_h[h] < MIN_EXCEEDANCES)
            for h in HORIZONS
        )
        if low_support:
            h_evento = None
        else:
            h_evento = first_crossing(event_skill_by_h, lambda v: v > 0)

        rows.append(
            {
                "dataset": dataset,
                "station_id": meta.get("station_id"),
                "station_name": meta.get("station_name"),
                "province": meta.get("province"),
                "model": model,
                "H_star_skill": h_skill,
                "H_star_evento": h_evento,  # NaN in the CSV = not defined (low support, <20 est. exceedances)
                "H_star_fidelidad": h_fidelidad,
                "H_star_skill_censored": h_skill == 7,
                "H_star_evento_censored": (h_evento == 7) if h_evento is not None else False,
                "H_star_fidelidad_censored": h_fidelidad == 7,
                "min_n_exceedances_est": round(min(v for v in n_exceed_by_h.values() if pd.notna(v)), 1)
                if any(pd.notna(v) for v in n_exceed_by_h.values())
                else None,
                "n_horizons_available": sum(1 for h in HORIZONS if h in g.index),
            }
        )

    out = pd.DataFrame(rows).sort_values(["dataset", "model"]).reset_index(drop=True)
    out_path = OUT_DIR / "h3_table.csv"
    out.to_csv(out_path, index=False)

    metadata = {
        "source_repo": SOURCE_REPO,
        "source_commit": SOURCE_COMMIT,
        "source_files": {
            "master_diagnostic_table.csv": sha256(MASTER),
            "exceedance_all_stations.csv": sha256(EXCEED),
        },
        "definitions": {
            "H_star_skill": "first-crossing, skill>0 for all j<=h, skill=1-RMSE_model/RMSE_persistence "
                             "(p32_ijf_ghostskill_hstar/src/diagnostics/hstar.py::compute_hstar(criterion='strict'))",
            "H_star_fidelidad": "first-crossing, alpha=Var(pred)/Var(true)>=0.5 for all j<=h "
                                 "(p32_ijf_ghostskill_hstar/src/diagnostics/variance.py, threshold matches "
                                 "scripts/15_decision_change_analysis.py ALPHA_PRIMARY)",
            "H_star_evento": "first-crossing, F1_model(abs_50) - F1_persistence(abs_50) > 0 for all j<=h; "
                              "abs_50 = 50 ug/m3 fixed threshold from scripts/03_exceedance_analysis.py; "
                              "NA if estimated exceedance count < 20 at any horizon in the common support; "
                              "CSI not implemented anywhere in source repo, F1 used instead (not invented, "
                              "it is the only composite event metric the repo actually computes)",
        },
        "known_deviation_from_frozen_protocol": (
            "H_star_skill uses persistence as the sole baseline. The frozen protocol required "
            "SS>0 against BOTH persistence and seasonal-naive; seasonal-naive-relative skill is "
            "not materialized as a column in any aggregated table in the source repo (only its own "
            "skill-vs-persistence is), so it is not computed here rather than approximated."
        ),
        "script": "scripts/compute_h3_table.py",
        "script_sha256": sha256(Path(__file__)),
        "output": str(out_path.relative_to(ROOT)),
        "n_rows": len(out),
        "n_datasets": out["dataset"].nunique(),
        "n_models": out["model"].nunique(),
    }
    meta_path = OUT_DIR / "h3_run_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))

    print(out.to_string(index=False))
    print(f"\nWrote {out_path} ({len(out)} rows) and {meta_path}")


if __name__ == "__main__":
    main()
