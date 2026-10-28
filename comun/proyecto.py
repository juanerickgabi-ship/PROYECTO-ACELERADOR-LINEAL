"""Rutas y entrada/salida de cada proyecto. Cada proyecto tiene la estructura
    Proyecto/README.md, datos/, src/, figuras/, resultados/, informe/
y sus scripts hacen  P = Proyecto(__file__)."""
import json
from pathlib import Path
import numpy as np
import pandas as pd


def _a_python(o):
    if isinstance(o, dict):
        return {str(k): _a_python(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_a_python(v) for v in o]
    if isinstance(o, np.ndarray):
        return _a_python(o.tolist())
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


class Proyecto:
    def __init__(self, archivo_script):
        self.src = Path(archivo_script).resolve().parent
        self.raiz = self.src.parent
        for d in ("datos", "resultados", "figuras", "informe"):
            p = self.raiz / d
            p.mkdir(exist_ok=True)
            setattr(self, d, p)

    # --- resultados resumidos (json) ---
    def guardar_json(self, nombre, dic):
        f = self.resultados / f"{nombre}.json"
        f.write_text(json.dumps(_a_python(dic), indent=1, ensure_ascii=False))
        print("  resultados", f.name)

    def cargar_json(self, nombre):
        return json.loads((self.resultados / f"{nombre}.json").read_text())

    # --- tablas (csv) en datos/ (datos simulados o de entrada) o resultados/ (analisis) ---
    def guardar_csv(self, df, nombre, carpeta="resultados"):
        f = getattr(self, carpeta) / f"{nombre}.csv"
        df.to_csv(f, index=False, float_format="%.6g")
        print(f"  {carpeta}", f.name)

    def leer_csv(self, nombre, carpeta="resultados", **kw):
        return pd.read_csv(getattr(self, carpeta) / f"{nombre}.csv", comment="#", **kw)

    def leer_parametros(self, nombre="parametros"):
        return json.loads((self.datos / f"{nombre}.json").read_text())
