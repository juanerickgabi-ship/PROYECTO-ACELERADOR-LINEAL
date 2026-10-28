"""Interaccion y transporte Monte Carlo de fotones (10 keV - 10 MeV).

Modelo:
  * mu_total(E) se interpola (log-log) en las tablas de comun/datos/atenuacion_fotones.csv;
  * la parte Compton se calcula con la seccion eficaz de Klein-Nishina por electron (exacta para electrones libres);
  * el resto, mu_abs = mu_total - mu_Compton, se trata como absorcion local (efecto fotoelectrico; por encima de
    ~2 MeV incluye la produccion de pares, que se aproxima tambien como absorcion local).
El transporte es vectorizado: todos los fotones vivos avanzan a la vez en cada iteracion.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

DATOS = Path(__file__).resolve().parent / "datos"
NA = 6.02214076e23          # 1/mol
RE = 2.8179403262e-13       # radio clasico del electron, cm
ME = 0.51099895             # MeV


# ----------------------------------------------------------------------------- Klein-Nishina
def sigma_kn(E):
    """seccion eficaz total de Klein-Nishina por electron (cm^2); E en MeV"""
    k = np.asarray(E, dtype=float) / ME
    l = np.log1p(2 * k)
    return 2 * np.pi * RE ** 2 * ((1 + k) / k ** 2 * (2 * (1 + k) / (1 + 2 * k) - l / k) + l / (2 * k) - (1 + 3 * k) / (1 + 2 * k) ** 2)


def energia_dispersada(E, cost):
    """energia del foton dispersado por Compton a un angulo de coseno cost"""
    return E / (1 + E / ME * (1 - cost))


def borde_compton(E):
    """energia maxima del electron Compton (retrodispersion, 180 grados)"""
    k = E / ME
    return E * 2 * k / (1 + 2 * k)


def dsigma_domega_kn(E, cost):
    """seccion eficaz diferencial de Klein-Nishina (cm^2/sr por electron)"""
    P = 1 / (1 + E / ME * (1 - cost))
    return 0.5 * RE ** 2 * P ** 2 * (P + 1 / P - (1 - cost ** 2))


def muestrear_kn(E, rng):
    """muestrea epsilon = E'/E y cos(theta) de Klein-Nishina (algoritmo de Geant4, G4KleinNishinaCompton),
    vectorizado por rechazo. Devuelve (E', cost)."""
    E = np.asarray(E, dtype=float)
    k = E / ME
    eps0 = 1 / (1 + 2 * k)
    eps02 = eps0 ** 2
    a1 = -np.log(eps0)
    a2 = a1 + 0.5 * (1 - eps02)
    eps = np.empty_like(E)
    cost = np.empty_like(E)
    pend = np.arange(E.size)
    while pend.size:
        r1, r2, r3 = rng.random((3, pend.size))
        rama = a1[pend] > a2[pend] * r1
        e = np.where(rama, np.exp(-a1[pend] * r2), np.sqrt(eps02[pend] + (1 - eps02[pend]) * r2))
        onecost = (1 - e) / (e * k[pend])
        sint2 = onecost * (2 - onecost)
        g = 1 - e * sint2 / (1 + e ** 2)
        ok = g >= r3
        eps[pend[ok]] = e[ok]
        cost[pend[ok]] = 1 - onecost[ok]
        pend = pend[~ok]
    return E * eps, np.clip(cost, -1, 1)


# ----------------------------------------------------------------------------- materiales
class Material:
    """material para fotones: mu en 1/cm"""
    _tabla = None

    def __init__(self, clave, rho=None):
        meta = json.loads((DATOS / "materiales_fotones.json").read_text())[clave]
        if Material._tabla is None:
            Material._tabla = pd.read_csv(DATOS / "atenuacion_fotones.csv", comment="#")
        t = Material._tabla[Material._tabla.material == clave].sort_values("E_MeV")
        self.clave, self.nombre = clave, meta["nombre"]
        self.rho = rho if rho is not None else meta["rho"]
        self.ZA = meta["ZA"]
        self.E = t.E_MeV.to_numpy()
        self.mr = t.mu_rho.to_numpy()
        self.mer = t.mu_en_rho.to_numpy()

    @staticmethod
    def _loglog(x, xs, ys):
        x = np.clip(np.asarray(x, dtype=float), xs[0], xs[-1])
        return np.exp(np.interp(np.log(x), np.log(xs), np.log(ys)))

    def mu_rho(self, E):
        return self._loglog(E, self.E, self.mr)

    def mu_en_rho(self, E):
        ok = np.isfinite(self.mer)
        return self._loglog(E, self.E[ok], self.mer[ok])

    def mu_total(self, E):
        return self.rho * self.mu_rho(E)

    def mu_compton(self, E):
        return np.minimum(self.rho * self.ZA * NA * sigma_kn(E), self.mu_total(E))

    def mu_abs(self, E):
        return self.mu_total(E) - self.mu_compton(E)


# ----------------------------------------------------------------------------- geometria
class Losa:
    """losa infinita en x, y entre z0 y z1"""
    def __init__(self, z0, z1):
        self.z0, self.z1 = z0, z1

    def distancia_salida(self, p, u):
        with np.errstate(divide="ignore", invalid="ignore"):
            d = np.where(u[:, 2] > 0, (self.z1 - p[:, 2]) / u[:, 2],
                         np.where(u[:, 2] < 0, (self.z0 - p[:, 2]) / u[:, 2], np.inf))
        return np.maximum(d, 0)


class Cilindro:
    """cilindro de radio R con eje z entre z0 y z1"""
    def __init__(self, R, z0, z1):
        self.R, self.z0, self.z1 = R, z0, z1

    def distancia_salida(self, p, u):
        dz = Losa(self.z0, self.z1).distancia_salida(p, u)
        a = u[:, 0] ** 2 + u[:, 1] ** 2
        b = 2 * (p[:, 0] * u[:, 0] + p[:, 1] * u[:, 1])
        c = p[:, 0] ** 2 + p[:, 1] ** 2 - self.R ** 2
        with np.errstate(divide="ignore", invalid="ignore"):
            dr = np.where(a > 1e-14, (-b + np.sqrt(np.maximum(b * b - 4 * a * c, 0))) / (2 * a), np.inf)
        return np.maximum(np.minimum(dz, dr), 0)


class Caja:
    """caja [x0,x1] x [y0,y1] x [z0,z1]"""
    def __init__(self, x0, x1, y0, y1, z0, z1):
        self.lo = np.array([x0, y0, z0], float)
        self.hi = np.array([x1, y1, z1], float)

    def distancia_salida(self, p, u):
        with np.errstate(divide="ignore", invalid="ignore"):
            d = np.where(u > 0, (self.hi - p) / u, np.where(u < 0, (self.lo - p) / u, np.inf))
        return np.maximum(d.min(axis=1), 0)


class Esfera:
    """esfera de radio R centrada en el origen"""
    def __init__(self, R):
        self.R = R

    def distancia_salida(self, p, u):
        b = (p * u).sum(1)
        c = (p * p).sum(1) - self.R ** 2
        return np.maximum(-b + np.sqrt(np.maximum(b * b - c, 0)), 0)


# ----------------------------------------------------------------------------- direcciones
def isotropas(n, rng):
    cost = 2 * rng.random(n) - 1
    phi = 2 * np.pi * rng.random(n)
    s = np.sqrt(1 - cost ** 2)
    return np.column_stack([s * np.cos(phi), s * np.sin(phi), cost])


def rotar(u, cost, phi):
    """gira las direcciones u un angulo polar acos(cost) y azimut phi alrededor de si mismas"""
    sint = np.sqrt(np.maximum(1 - cost ** 2, 0))
    ux, uy, uz = u[:, 0], u[:, 1], u[:, 2]
    s = np.sqrt(np.maximum(1 - uz ** 2, 0))
    cp, sp = np.cos(phi), np.sin(phi)
    normal = s > 1e-6
    with np.errstate(divide="ignore", invalid="ignore"):
        nx = np.where(normal, sint * (ux * uz * cp - uy * sp) / s + ux * cost, sint * cp)
        ny = np.where(normal, sint * (uy * uz * cp + ux * sp) / s + uy * cost, sint * sp)
        nz = np.where(normal, -sint * cp * s + uz * cost, np.sign(uz + 1e-300) * cost)
    v = np.column_stack([nx, ny, nz])
    return v / np.linalg.norm(v, axis=1, keepdims=True)


# ----------------------------------------------------------------------------- transporte
def transportar(mat, geom, E, pos, u, rng, E_corte=0.010, max_iter=500):
    """Transporta fotones (E en MeV, pos en cm, u unitarios) dentro de la geometria hasta que escapan o se absorben.
    Devuelve dos diccionarios de arreglos:
      inter: ev, x, y, z, tipo (0 absorcion, 1 Compton), Eg (energia del foton antes), Ee (energia del electron,
             depositada localmente), uex, uey, uez (direccion del electron)
      esc:   ev, E, x, y, z, ux, uy, uz, n_disp (numero de dispersiones Compton previas)"""
    E = np.array(E, dtype=float)
    pos = np.array(pos, dtype=float)
    u = np.array(u, dtype=float)
    ev = np.arange(E.size)
    nd = np.zeros(E.size, int)
    I, S = [], []
    for _ in range(max_iter):
        if E.size == 0:
            break
        mu = mat.mu_total(E)
        s = -np.log(rng.random(E.size)) / mu
        d = geom.distancia_salida(pos, u)
        sale = s >= d
        if sale.any():
            q = pos[sale] + d[sale, None] * u[sale]
            S.append(np.column_stack([ev[sale], E[sale], q, u[sale], nd[sale]]))
        k = ~sale
        E, pos, u, ev, nd, s = E[k], pos[k], u[k], ev[k], nd[k], s[k]
        pos = pos + s[:, None] * u
        pc = mat.mu_compton(E) / mat.mu_total(E)
        comp = (rng.random(E.size) < pc) & (E > E_corte)
        # absorcion (fotoelectrico o foton por debajo del corte): toda la energia es local
        a = ~comp
        if a.any():
            I.append(np.column_stack([ev[a], pos[a], np.zeros(a.sum()), E[a], E[a], u[a]]))
        # Compton
        Ec, pc_, uc, evc, ndc = E[comp], pos[comp], u[comp], ev[comp], nd[comp]
        if Ec.size:
            Ep, cost = muestrear_kn(Ec, rng)
            phi = 2 * np.pi * rng.random(Ec.size)
            Te = Ec - Ep
            # direccion del electron: cot(phi_e) = (1+k) tan(theta/2), azimut opuesto
            th = np.arccos(cost)
            phe = np.arctan2(1.0, (1 + Ec / ME) * np.tan(th / 2))
            ue = rotar(uc, np.cos(phe), phi + np.pi)
            I.append(np.column_stack([evc, pc_, np.ones(Ec.size), Ec, Te, ue]))
            uc = rotar(uc, cost, phi)
            Ec = Ep
        E, pos, u, ev, nd = Ec, pc_, uc, evc, ndc + 1
    col_i = ["ev", "x", "y", "z", "tipo", "Eg", "Ee", "uex", "uey", "uez"]
    col_s = ["ev", "E", "x", "y", "z", "ux", "uy", "uz", "n_disp"]
    I = np.vstack(I) if I else np.empty((0, len(col_i)))
    S = np.vstack(S) if S else np.empty((0, len(col_s)))
    inter = {c: I[:, j] for j, c in enumerate(col_i)}
    esc = {c: S[:, j] for j, c in enumerate(col_s)}
    inter["ev"] = inter["ev"].astype(int)
    esc["ev"] = esc["ev"].astype(int)
    return inter, esc


def energia_por_evento(inter, n):
    """energia depositada (MeV) por evento, sumando los electrones locales"""
    return np.bincount(inter["ev"], weights=inter["Ee"], minlength=n)
