"""Fisica de neutrones: cinematica de la dispersion elastica, seccion eficaz n-p y propiedades de materiales."""
from pathlib import Path
import numpy as np
import pandas as pd

DATOS = Path(__file__).resolve().parent / "datos"
NA = 6.02214076e23
BARN = 1e-24
V0 = 2200.0               # m/s, velocidad del neutron termico de 0,0253 eV
E_TERMICA = 0.0253e-6     # MeV


def secciones():
    return pd.read_csv(DATOS / "neutrones_secciones.csv", comment="#").set_index("elemento")


def sigma_np(E):
    """seccion eficaz elastica n-p (barn) en funcion de la energia del neutron en MeV (laboratorio).
    Parametrizacion de rango efectivo (singlete + triplete) usada en textos de fisica nuclear:
    20,4 b para E -> 0 y 2,9 b a 2 MeV. Valida aproximadamente de 1 eV a 20 MeV."""
    E = np.asarray(E, dtype=float)
    return (3 * np.pi / (1.206 * E + (-1.86 + 0.09415 * E + 0.0001306 * E ** 2) ** 2)
            + np.pi / (1.206 * E + (0.4223 + 0.13 * E) ** 2))


def alfa(A):
    """fraccion minima de energia tras una colision elastica: E'/E >= alfa"""
    return ((A - 1) / (A + 1)) ** 2


def xi(A):
    """decremento logaritmico medio de energia por colision"""
    a = alfa(A)
    return 1.0 if A == 1 else 1 + a * np.log(a) / (1 - a)


def colision_elastica(E, A, rng):
    """dispersion elastica isotropa en el centro de masa: devuelve (E', cos_lab, mu_cm)"""
    A = np.asarray(A, dtype=float)
    mu = 2 * rng.random(np.size(E)) - 1
    q = A ** 2 + 2 * A * mu + 1
    Ep = E * q / (A + 1) ** 2
    cos_lab = (1 + A * mu) / np.sqrt(q)
    return Ep, cos_lab, mu


def densidad_atomica(rho, composicion):
    """densidad atomica (atomos/cm3) de cada elemento para un compuesto o mezcla dada por fracciones masicas
    composicion = {elemento: fraccion_masica}"""
    S = secciones()
    return {el: rho * w * NA / S.loc[el, "A"] for el, w in composicion.items()}


def fracciones_masicas(formula):
    """fracciones masicas de una formula {elemento: numero de atomos}"""
    S = secciones()
    m = {el: n * S.loc[el, "A"] for el, n in formula.items()}
    tot = sum(m.values())
    return {el: v / tot for el, v in m.items()}
