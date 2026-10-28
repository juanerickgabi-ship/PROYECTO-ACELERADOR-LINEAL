"""Figuras del Proyecto 19 (acelerador lineal)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import numpy as np
from comun.proyecto import Proyecto
from comun import estilo

P = Proyecto(__file__)
par = P.leer_parametros()
r = P.cargar_json("resumen")

# Fig 1: diseno
D = P.leer_csv("diseno_celdas")
fig, axs = estilo.figura(1, 2, alto=3.7)
axs[0].plot(D.celda, D.T_entrada_MeV, "o-", ms=3)
axs[0].set_xlabel("Hueco n")
axs[0].set_ylabel("Energía del síncrono (MeV)")
estilo.letra(axs[0], "(a)", 0.03)
axs[1].plot(D.celda, 100 * D.L_celda_m, "s-", ms=3, color="#d1495b")
axs[1].set_xlabel("Celda n")
axs[1].set_ylabel("Longitud de la celda βλ (cm)")
estilo.letra(axs[1], "(b)", 0.03)
estilo.guardar(fig, P, "fig01_diseno")

# Fig 2: espacio de fases longitudinal
fig, axs = estilo.figura(2, 3, alto=6.4)
for fila, ps in enumerate((par["fase_referencia_grados"], 30)):
    d = np.load(P.datos / f"paquete_fase{ps}.npz")
    nmax = d["dP"].shape[0] - 1
    for col, k in enumerate((0, nmax // 2, nmax)):
        ax = axs[fila, col]
        ax.plot(d["dP"][k], 1000 * d["dW"][k], ".", ms=1.5, alpha=0.6)
        ax.set_xlim(-120, 120)
        ax.set_ylim(-2500, 2500)
        ax.set_title(f"φs = {ps}°, hueco {k}", fontsize=10)
        if fila == 1:
            ax.set_xlabel("Δφ (grados)")
        if col == 0:
            ax.set_ylabel("ΔW (keV)")
estilo.guardar(fig, P, "fig02_espacio_fases")

# Fig 3: oscilaciones de sincrotron
O = P.leer_csv("oscilacion_pequena")
MU = P.leer_csv("avance_sincrotron")
EST = P.leer_csv("estabilidad_fase")
fig, axs = estilo.figura(1, 2, alto=3.8)
axs[0].plot(O.celda, O.dphi, "o-", ms=3)
axs[0].axhline(0, color="k", lw=0.7)
axs[0].set_xlabel("Hueco n")
axs[0].set_ylabel("Δφ (grados), amplitud inicial 3°")
estilo.letra(axs[0], "(a)", 0.9)
axs[1].plot(O.celda, np.degrees(O.mu_teo_rad), "-", label="teoría (pequeña amplitud)")
axs[1].plot(MU.celda_media, np.degrees(MU.mu_sim), "o", label="simulación")
axs[1].set_xlabel("Hueco n")
axs[1].set_ylabel("Avance de fase por celda (grados)")
axs[1].legend()
estilo.letra(axs[1], "(b)", 0.9, 0.5)
estilo.guardar(fig, P, "fig03_sincrotron")

# Fig 4: estabilidad, error de frecuencia y electrones
ER = P.leer_csv("error_frecuencia")
E = P.leer_csv("electrones")
fig, axs = estilo.figura(1, 3, alto=3.6)
axs[0].plot(EST.fase_sincrona, 100 * EST.capturadas, "o-", label="junto al síncrono")
axs[0].plot(EST.fase_sincrona, 100 * EST.aceleradas, "s--", label="con la energía final")
axs[0].legend(fontsize=7.5, loc="lower left")
axs[0].set_xlabel("Fase síncrona φs (grados)")
axs[0].set_ylabel("Partículas en el paquete (%)")
axs[1].semilogx(100 * ER.error_f[1:], 100 * ER.capturadas[1:], "s-", label="capturadas (%)")
axs[1].set_xlabel("Error de frecuencia (%)")
axs[1].set_ylabel("Capturadas (%)")
ax2 = axs[1].twinx()
ax2.semilogx(100 * ER.error_f[1:], ER.fase_media_final[1:], "^--", color="#d1495b")
ax2.set_ylabel("Desplazamiento de fase (°)", color="#d1495b")
ax2.spines["right"].set_visible(True)
ax2.grid(False)
for p in (-40, -20, 0, 20, 40):
    axs[2].plot(E.celda, E[f"T_fase{p}"], label=f"φ = {p}°")
axs[2].set_xlabel("Celda")
axs[2].set_ylabel("Energía del electrón (MeV)")
axs[2].legend(fontsize=7.5)
for ax, l in zip(axs, "abc"):
    estilo.letra(ax, f"({l})", 0.03)
estilo.guardar(fig, P, "fig04_estabilidad_electrones")
