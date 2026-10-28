"""Poder de frenado de particulas cargadas.

  * Particulas pesadas (p, alfa, muon, pion): formula de Bethe-Bloch con correccion de densidad de Sternheimer
    (sin correcciones de capas, por lo que pierde validez para protones de menos de ~1 MeV).
  * Electrones: poder de frenado de colision de Rohrlich-Carlson (ICRU 37) y una estimacion sencilla del radiativo.
  * Alcance CSDA por integracion numerica de 1/S y distribucion de Landau para capas delgadas.
"""
import numpy as np

K = 0.307075          # MeV cm^2 / mol  (4 pi N_A r_e^2 m_e c^2)
ME = 0.51099895       # MeV
MASAS = {"electron": ME, "muon": 105.6583755, "pion": 139.57039, "kaon": 493.677, "proton": 938.27208816,
         "deuteron": 1875.612928, "alfa": 3727.3794066}
CARGAS = {"electron": 1, "muon": 1, "pion": 1, "kaon": 1, "proton": 1, "deuteron": 1, "alfa": 2}

# ZA (mol/g), I (eV), rho (g/cm3), Z efectivo, parametros de Sternheimer (Cbar, x0, x1, a, k, delta0)
MATERIALES = {
    "agua":     dict(nombre="Agua", ZA=0.55508, I=75.0, rho=1.0, Zef=7.42, st=(3.5017, 0.2400, 2.8004, 0.09116, 3.4773, 0.0)),
    "aire":     dict(nombre="Aire", ZA=0.49919, I=85.7, rho=1.205e-3, Zef=7.6, st=(10.5961, 1.7418, 4.2759, 0.10914, 3.3994, 0.0)),
    "silicio":  dict(nombre="Silicio", ZA=0.49848, I=173.0, rho=2.329, Zef=14, st=(4.4355, 0.2015, 2.8716, 0.14921, 3.2546, 0.14)),
    "aluminio": dict(nombre="Aluminio", ZA=0.48181, I=166.0, rho=2.699, Zef=13, st=(4.2395, 0.1708, 3.0127, 0.08024, 3.6345, 0.12)),
    "cobre":    dict(nombre="Cobre", ZA=0.45636, I=322.0, rho=8.96, Zef=29, st=(4.4190, -0.0254, 3.2792, 0.14339, 2.9044, 0.08)),
    "plomo":    dict(nombre="Plomo", ZA=0.39575, I=823.0, rho=11.35, Zef=82, st=(6.2018, 0.3776, 3.8073, 0.09359, 3.1608, 0.14)),
    "PVT":      dict(nombre="Centellador plástico (PVT)", ZA=0.54141, I=64.7, rho=1.032, Zef=5.7, st=(3.1997, 0.1464, 2.4855, 0.16101, 3.2393, 0.0)),
    "NaI":      dict(nombre="NaI", ZA=0.42697, I=452.0, rho=3.667, Zef=50, st=(6.0572, 0.1203, 3.5920, 0.12516, 3.0398, 0.0)),
    "hueso":    dict(nombre="Hueso cortical", ZA=0.51478, I=106.4, rho=1.85, Zef=13.8, st=None),
    "musculo":  dict(nombre="Músculo", ZA=0.54938, I=75.3, rho=1.05, Zef=7.6, st=None),
    "pulmon":   dict(nombre="Pulmón", ZA=0.54965, I=75.3, rho=0.26, Zef=7.6, st=None),
}


def cinematica(T, m):
    """beta, gamma, beta*gamma para energia cinetica T y masa m (MeV)"""
    T = np.asarray(T, dtype=float)
    g = 1 + T / m
    b = np.sqrt(1 - 1 / g ** 2)
    return b, g, b * g


def delta_densidad(bg, mat):
    """correccion de densidad de Sternheimer delta(beta*gamma)"""
    if mat["st"] is None:
        return np.zeros_like(bg)
    C, x0, x1, a, k, d0 = mat["st"]
    x = np.log10(bg)
    return np.where(x >= x1, 2 * np.log(10) * x - C,
                    np.where(x >= x0, 2 * np.log(10) * x - C + a * (x1 - x) ** k, d0 * 10 ** (2 * (x - x0))))


def tmax(T, m):
    """energia maxima transferible a un electron en una colision"""
    b, g, bg = cinematica(T, m)
    r = ME / m
    return 2 * ME * bg ** 2 / (1 + 2 * g * r + r ** 2)


def bethe(T, particula="proton", material="agua", densidad=True):
    """poder de frenado masico de colision (MeV cm^2/g) de Bethe-Bloch para particulas pesadas"""
    mat = MATERIALES[material]
    m, z = MASAS[particula], CARGAS[particula]
    b, g, bg = cinematica(T, m)
    I = mat["I"] * 1e-6
    d = delta_densidad(bg, mat) if densidad else 0
    L = 0.5 * np.log(2 * ME * bg ** 2 * tmax(T, m) / I ** 2) - b ** 2 - d / 2
    return K * z ** 2 * mat["ZA"] / b ** 2 * np.maximum(L, 1e-3)


def electron_colision(T, material="agua"):
    """poder de frenado masico de colision de electrones (Rohrlich-Carlson, ICRU 37), MeV cm^2/g"""
    mat = MATERIALES[material]
    T = np.asarray(T, dtype=float)
    tau = T / ME
    b, g, bg = cinematica(T, ME)
    I = mat["I"] * 1e-6 / ME
    F = 1 - b ** 2 + (tau ** 2 / 8 - (2 * tau + 1) * np.log(2)) / (tau + 1) ** 2
    d = delta_densidad(bg, mat)
    return K / 2 * mat["ZA"] / b ** 2 * (np.log(tau ** 2 * (tau + 2) / (2 * I ** 2)) + F - d)


def electron_radiativo(T, material="agua"):
    """estimacion del poder de frenado radiativo: S_rad/S_col ~ Z_ef (T + m c^2) / 800 MeV"""
    mat = MATERIALES[material]
    return electron_colision(T, material) * mat["Zef"] * (np.asarray(T) + ME) / 800.0


def electron_total(T, material="agua"):
    return electron_colision(T, material) + electron_radiativo(T, material)


def alcance_csda(T, S_funcion, T_min=1e-3, n=4000, p=1.75):
    """alcance CSDA (g/cm^2) R(T) = R(T_min) + integral de dT/S(T) desde T_min; S en MeV cm^2/g.
    R(T_min) se estima con una ley de potencias R ~ T^p. Devuelve R evaluado en los T pedidos."""
    T = np.atleast_1d(np.asarray(T, dtype=float))
    Tg = np.geomspace(T_min, T.max(), n)
    inv = 1 / S_funcion(Tg)
    R = np.concatenate([[0], np.cumsum(0.5 * (inv[1:] + inv[:-1]) * np.diff(Tg))])
    R += T_min / (p * S_funcion(np.array([T_min]))[0])
    return np.interp(T, Tg, R)


def landau_mpv(T, espesor_cm, particula="muon", material="silicio"):
    """valor mas probable de la perdida de energia en una capa delgada (Landau-Vavilov-Bichsel), MeV"""
    mat = MATERIALES[material]
    m, z = MASAS[particula], CARGAS[particula]
    b, g, bg = cinematica(T, m)
    xi = K / 2 * mat["ZA"] * z ** 2 * espesor_cm * mat["rho"] / b ** 2
    I = mat["I"] * 1e-6
    return xi * (np.log(2 * ME * bg ** 2 / I) + np.log(xi / I) + 0.200 - b ** 2 - delta_densidad(bg, mat)), xi
