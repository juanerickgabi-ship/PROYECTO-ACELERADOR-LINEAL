"""Acelerador lineal de tubos de deriva: la particula gana Delta E = q V cos(phi) en cada hueco; las celdas se disenan
para la particula sincrona (L_n = beta_n lambda). Dinamica longitudinal de un paquete de particulas."""
import numpy as np

C = 299792458.0
MASAS = {"prot(*@\'o@*)n": 938.27208816, "electr(*@\'o@*)n": 0.51099895}


def beta_de_T(T, m):
    g = 1 + T / m
    return np.sqrt(1 - 1 / g ** 2)


def disenar(T0, Tfin, qV, phis_grados, m, lam, max_celdas=10000):
    """celdas de la particula sincrona: energia a la entrada de cada hueco y longitud de la celda siguiente"""
    T, Ts, L = T0, [], []
    for _ in range(max_celdas):
        Ts.append(T)
        T = T + qV * np.cos(np.radians(phis_grados))
        L.append(beta_de_T(T, m) * lam)
        if T >= Tfin:
            break
    return np.array(Ts), np.array(L)


def seguir(T0, dphi0_grados, L, qV, phis_grados, m, f_rf, error_f=0.0):
    """sigue particulas (arreglos T0 en MeV y desfases iniciales en grados) a traves de las celdas L (m).
    La fase en cada hueco es phi = phi_s + omega (t - t_s), con omega la frecuencia real del RF (con error relativo error_f).
    Devuelve energia y fase (grados, relativa a la cresta) en cada hueco: matrices (celdas+1, N)."""
    w = 2 * np.pi * f_rf * (1 + error_f)
    T = np.array(T0, float)
    phi = np.radians(phis_grados + np.array(dphi0_grados, float))
    TT, PP = [T.copy()], [np.degrees(phi)]
    for Ln in L:
        T = T + qV * np.cos(phi)
        T = np.maximum(T, 1e-6)
        dt = Ln / (beta_de_T(T, m) * C)
        # en el diseno, el sincrono tarda exactamente un periodo del RF de diseno por celda (L = beta lambda)
        phi = phi + w * dt - 2 * np.pi
        TT.append(T.copy())
        PP.append(np.degrees(phi))
    return np.array(TT), np.array(PP)


def avance_sincrotron(qV, phis_grados, T, m):
    """avance de fase de las oscilaciones de sincrotron por celda (rad), pequena amplitud:
    mu^2 = 2 pi qV (-sin phi_s) / (m c^2 beta^2 gamma^3)"""
    g = 1 + T / m
    b = beta_de_T(T, m)
    return np.sqrt(np.maximum(2 * np.pi * qV * (-np.sin(np.radians(phis_grados))) / (m * b ** 2 * g ** 3), 0))


def aceptancia_fase(phis_grados):
    """extremos de la separatriz en fase: phi_2 (anterior) y -phi_s (posterior) para el potencial del pendulo"""
    from scipy.optimize import brentq
    ps = np.radians(phis_grados)
    f = lambda p: np.sin(p) - p * np.cos(ps) - (np.sin(-ps) - (-ps) * np.cos(ps))
    try:
        p2 = brentq(f, -np.pi, ps)
    except ValueError:
        p2 = np.nan
    return np.degrees(p2), -phis_grados
