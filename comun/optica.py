"""Optica para los proyectos Cherenkov: indice de refraccion, condicion y angulo de Cherenkov, Frank-Tamm y
eficiencia cuantica aproximada de un fotocatodo bialcalino."""
import numpy as np

ALFA = 1 / 137.035999084
MASAS = {"electrón": 0.51099895, "muón": 105.6583755, "pión": 139.57039, "kaón": 493.677, "protón": 938.27208816}

# indices de refraccion de referencia (a ~ 400-550 nm)
INDICES = {"aire": 1.000293, "CO₂": 1.00045, "aerogel 1,01": 1.01, "aerogel 1,03": 1.03, "aerogel 1,05": 1.05,
           "agua": 1.333, "hielo": 1.31, "acrílico": 1.49, "vidrio de plomo": 1.65, "diamante": 2.42}


def n_agua(lam_nm):
    """indice del agua a 20 C, formula de Cauchy ajustada a n(404,7 nm) = 1,3429 y n(656,3 nm) = 1,3312"""
    lam = np.asarray(lam_nm, dtype=float)
    return 1.3240 + 3092.0 / lam ** 2


def beta_de_T(T, m):
    g = 1 + np.asarray(T, dtype=float) / m
    return np.sqrt(1 - 1 / g ** 2)


def beta_de_p(p, m):
    p = np.asarray(p, dtype=float)
    return p / np.sqrt(p ** 2 + m ** 2)


def emite(beta, n):
    return np.asarray(beta) * n > 1


def angulo(beta, n):
    """angulo de Cherenkov (rad); nan si no hay emision"""
    c = 1 / (np.asarray(beta, dtype=float) * n)
    return np.where(c < 1, np.arccos(np.minimum(c, 1)), np.nan)


def gamma_umbral(n):
    return 1 / np.sqrt(1 - 1 / n ** 2)


def umbrales(m, n):
    """energia total, cinetica y momento umbral (MeV, MeV/c)"""
    g = gamma_umbral(n)
    E = g * m
    return E, E - m, m / np.sqrt(n ** 2 - 1)


def frank_tamm_dndxdl(lam_nm, beta, n):
    """d2N/dx dlambda (fotones / cm / nm)"""
    lam_cm = np.asarray(lam_nm, dtype=float) * 1e-7
    s2 = np.maximum(1 - 1 / (beta ** 2 * np.asarray(n) ** 2), 0)
    return 2 * np.pi * ALFA / lam_cm ** 2 * s2 * 1e-7


def eficiencia_cuantica(lam_nm):
    """eficiencia cuantica aproximada de un fotocatodo bialcalino con ventana de borosilicato (tipo R5912)"""
    l = [270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 700]
    q = [0.00, 0.12, 0.22, 0.25, 0.26, 0.25, 0.22, 0.18, 0.13, 0.09, 0.06, 0.035, 0.018, 0.008, 0.0]
    return np.interp(lam_nm, l, q, left=0, right=0)


def muestrear_lambda(n, l1, l2, rng):
    """longitudes de onda con densidad ~ 1/lambda^2 en [l1, l2] (espectro de Frank-Tamm con n constante)"""
    u = rng.random(n)
    return 1 / (1 / l1 - u * (1 / l1 - 1 / l2))
