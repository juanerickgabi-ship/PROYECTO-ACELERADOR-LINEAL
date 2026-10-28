"""Proyecto 19: acelerador lineal de protones (tipo Alvarez) de 3 a 50 MeV.
1) diseno de las celdas para la particula sincrona y energia frente al numero de cavidades;
2) paquete de particulas: estabilidad de fase para distintas fases sincronas;
3) oscilaciones de sincrotron: avance de fase simulado frente a la teoria;
4) efecto de un error de frecuencia (sincronizacion); 5) electrones (beta ~ 1)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import numpy as np
import pandas as pd
from comun.proyecto import Proyecto
import modelo as M

P = Proyecto(__file__)
par = P.leer_parametros()
rng = np.random.default_rng(par["semilla"])
m = M.MASAS[par["particula"]]
f = par["f_rf_MHz"] * 1e6
lam = M.C / f
qV = par["V_gap_MV"]
T0, Tf = par["T_inicial_MeV"], par["T_final_MeV"]
res = dict(lambda_m=lam)

# 1) diseno
Ts, L = M.disenar(T0, Tf, qV, par["fase_referencia_grados"], m, lam)
P.guardar_csv(pd.DataFrame({"celda": np.arange(len(L)), "T_entrada_MeV": Ts, "L_celda_m": L, "beta": M.beta_de_T(Ts, m)}), "diseno_celdas")
res["diseno"] = dict(celdas=len(L), longitud_m=float(L.sum()), L_primera=float(L[0]), L_ultima=float(L[-1]),
                     gradiente_MeV_m=float((Tf - T0) / L.sum()), ganancia_por_celda=qV * np.cos(np.radians(par["fase_referencia_grados"])))
# ecuacion de la guia: E_N = E_0 + sum q V cos(phi_i), ilustrada con la fase sincrona en cada celda
filas = []
for ps in par["fases_sincronas_grados"]:
    Tsx, Lx = M.disenar(T0, Tf, qV, ps, m, lam) if ps < 90 else (None, None)
    filas.append(dict(fase_sincrona=ps, celdas=len(Lx), longitud_m=Lx.sum(), aceptancia=M.aceptancia_fase(ps)))
P.guardar_csv(pd.DataFrame([{k: (v if k != "aceptancia" else None) for k, v in f_.items()} for f_ in filas]).drop(columns="aceptancia"), "celdas_vs_fase")

# 2) paquetes para cada fase sincrona (cada uno con su propio diseno)
h = par["haz"]
N = h["particulas"]
dphi0 = h["dispersion_fase_grados"] * rng.standard_normal(N)
dT0 = T0 * h["dispersion_energia_rel"] * rng.standard_normal(N)
filas = []
for ps in par["fases_sincronas_grados"]:
    Tsx, Lx = M.disenar(T0, Tf, qV, ps, m, lam)
    TT, PP = M.seguir(T0 + dT0, dphi0, Lx, qV, ps, m, f)
    Tsync = np.concatenate([Tsx, [Tsx[-1] + qV * np.cos(np.radians(ps))]])
    dW = TT - Tsync[:, None]
    dP = PP - ps
    capt = np.abs(dP[-1]) < 60
    acel = np.abs(dW[-1]) < 1.0                     # llegan con la energia de diseno (+-1 MeV)
    filas.append(dict(fase_sincrona=ps, celdas=len(Lx), capturadas=capt.mean(), aceleradas=acel.mean(),
                      fase_media_final_aceleradas=float(PP[-1, acel].mean()) if acel.any() else np.nan, dW_rms_final_MeV=dW[-1, capt].std() if capt.any() else np.nan,
                      dphi_rms_final=dP[-1, capt].std() if capt.any() else np.nan, dphi_rms_inicial=dP[0].std(),
                      T_medio_final=TT[-1, capt].mean() if capt.any() else np.nan))
    np.savez_compressed(P.datos / f"paquete_fase{ps}.npz", dP=dP[:, :800].astype(np.float32), dW=dW[:, :800].astype(np.float32))
EST = pd.DataFrame(filas)
P.guardar_csv(EST, "estabilidad_fase")

# 3) oscilacion de pequena amplitud con la fase de referencia
ps = par["fase_referencia_grados"]
TT, PP = M.seguir(np.array([T0]), np.array([3.0]), L, qV, ps, m, f)
dp = PP[:, 0] - ps
cruces = np.where(np.diff(np.sign(dp)) != 0)[0]
mu_teo = M.avance_sincrotron(qV, ps, Ts, m)
P.guardar_csv(pd.DataFrame({"celda": np.arange(len(dp)), "dphi": dp, "mu_teo_rad": np.append(mu_teo, mu_teo[-1])}), "oscilacion_pequena")
# avance de fase simulado: media vuelta entre cruces por cero consecutivos
filas = []
for a, b in zip(cruces[:-1], cruces[1:]):
    filas.append(dict(celda_media=(a + b) / 2, mu_sim=np.pi / (b - a), mu_teo=mu_teo[int((a + b) / 2)]))
MU = pd.DataFrame(filas)
P.guardar_csv(MU, "avance_sincrotron")
res["sincrotron"] = dict(mu_inicial_teo_grados=float(np.degrees(mu_teo[0])), mu_final_teo_grados=float(np.degrees(mu_teo[-1])),
                         amplitud_inicial=float(abs(dp[:5]).max()), amplitud_final=float(abs(dp[-10:]).max()))

# 4) error de frecuencia
filas = []
for ef in par["error_frecuencia_rel"]:
    TT, PP = M.seguir(T0 + dT0, dphi0, L, qV, ps, m, f, error_f=ef)
    capt = np.abs(PP[-1] - ps) < 60
    filas.append(dict(error_f=ef, capturadas=capt.mean(), T_medio_final=TT[-1, capt].mean() if capt.any() else np.nan,
                      fase_media_final=(PP[-1, capt] - ps).mean() if capt.any() else np.nan))
    np.save(P.datos / f"fase_media_error{ef}.npy", np.median(PP - ps, axis=1).astype(np.float32))
ER = pd.DataFrame(filas)
P.guardar_csv(ER, "error_frecuencia")

# 5) electrones: celdas de longitud lambda (beta ~ 1), fase fija
e = par["electron"]
me = M.MASAS["electrón"]
Le = np.full(e["celdas"], lam)
TT, PP = M.seguir(np.full(5, e["T_inicial_MeV"]), np.array([-40, -20, 0, 20, 40.0]), Le, qV, 0.0, me, f)
P.guardar_csv(pd.DataFrame({"celda": np.arange(len(TT)), **{f"T_fase{p:g}": TT[:, i] for i, p in enumerate([-40, -20, 0, 20, 40])},
                            **{f"fase{p:g}": PP[:, i] for i, p in enumerate([-40, -20, 0, 20, 40])}}), "electrones")
res["electrones"] = dict(T_final_cresta=float(TT[-1, 2]), deriva_fase_cresta=float(PP[-1, 2] - PP[0, 2]), T_final_40=float(TT[-1, 4]),
                         cos40=float(np.cos(np.radians(40))))
P.guardar_json("resumen", res)
print(res)
print(EST.to_string())
print(ER.to_string())
print(MU.head(8).to_string())
