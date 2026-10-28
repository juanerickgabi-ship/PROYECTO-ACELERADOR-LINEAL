"""Informe, presentacion y README del Proyecto 19 (acelerador lineal)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import numpy as np
from comun.proyecto import Proyecto
from comun.latex import num, sig, pct, pm, rellenar, figura, tabla, escribir_informe, presentacion, escribir_readme

P = Proyecto(__file__)
par = P.leer_parametros()
r = P.cargar_json("resumen")
EST = P.leer_csv("estabilidad_fase").set_index("fase_sincrona")
ER = P.leer_csv("error_frecuencia").set_index("error_f")
MU = P.leer_csv("avance_sincrotron")
d, s, e = r["diseno"], r["sincrotron"], r["electrones"]
v = dict(f=num(par["f_rf_MHz"], 1), lam=num(100 * r["lambda_m"], 1), qV=num(par["V_gap_MV"], 1), T0=num(par["T_inicial_MeV"], 0),
         Tf=num(par["T_final_MeV"], 0), N=str(d["celdas"]), Ltot=num(d["longitud_m"], 2), L1=num(100 * d["L_primera"], 1),
         L2=num(100 * d["L_ultima"], 1), grad=num(d["gradiente_MeV_m"], 2), gan=num(d["ganancia_por_celda"], 3),
         c30=pct(EST.loc[-30, "capturadas"], 1), c60=pct(EST.loc[-60, "capturadas"], 1), c0=pct(EST.loc[0, "capturadas"], 1),
         a0=pct(EST.loc[0, "aceleradas"], 1), a30p=pct(EST.loc[30, "aceleradas"], 1), fm30p=num(EST.loc[30, "fase_media_final_aceleradas"], 0),
         c15=pct(EST.loc[-15, "capturadas"], 1), N60=str(int(EST.loc[-60, "celdas"])), N0=str(int(EST.loc[0, "celdas"])),
         dphi0=num(EST.loc[-30, "dphi_rms_inicial"], 1), dphi30=num(EST.loc[-30, "dphi_rms_final"], 1), dW30=num(1000 * EST.loc[-30, "dW_rms_final_MeV"], 0),
         mu0=num(s["mu_inicial_teo_grados"], 1), mu1=num(s["mu_final_teo_grados"], 1), amp0=num(s["amplitud_inicial"], 1), amp1=num(s["amplitud_final"], 2),
         musim=num(np.degrees(MU.mu_sim.iloc[0]), 1), muteo=num(np.degrees(MU.mu_teo.iloc[0]), 1),
         e1=pct(ER.loc[0.01, "capturadas"], 1), e2=pct(ER.loc[0.02, "capturadas"], 1), e4=pct(ER.loc[0.04, "capturadas"], 1),
         fs1=num(ER.loc[0.01, "fase_media_final"], 1), Te1=num(ER.loc[0.01, "T_medio_final"], 2),
         eT=num(e["T_final_cresta"], 2), eT40=num(e["T_final_40"], 2), ed=num(e["deriva_fase_cresta"], 1),
         nE=str(par["electron"]["celdas"]), eTi=num(par["electron"]["T_inicial_MeV"], 0))
meta = dict(numero=19, titulo="Acelerador lineal", area="Aceleradores", nivel="III")
meta["resumen"] = rellenar(r"""Se modela un acelerador lineal de tubos de deriva para protones a @f@~MHz en el que cada cavidad aporta
$\Delta E=qV\cos\phi$, de modo que tras $N$ cavidades $E_N=E_0+\sum qV_i\cos\phi_i$. Se diseñan las celdas para la partícula
síncrona ($L_n=\beta_n\lambda$): con $qV=@qV@$~MeV y $\phi_s=-30°$ se pasa de @T0@ a @Tf@~MeV en @N@ celdas y @Ltot@~m. Siguiendo un
paquete de \num{3000} partículas con dispersión de fase y energía se estudia la estabilidad de fase: con $\phi_s=-30°$ el @c30@ del
paquete permanece agrupado y realiza oscilaciones de sincrotrón cuyo avance de fase coincide con la teoría de pequeña amplitud,
mientras que en la cresta ($\phi_s=0$) solo el @a0@ llega a la energía final. Se estudian además el efecto de un error en la
frecuencia del RF y el caso de los electrones, que viajan a $\beta\simeq1$ y no tienen oscilaciones de fase.""", v)

filas = [[f"{ps:+d}" if ps else "0", str(int(f.celdas)), pct(f.capturadas, 1), pct(f.aceleradas, 1), num(f.dphi_rms_final, 1), num(1000 * f.dW_rms_final_MeV, 0)]
         for ps, f in EST.iterrows()]
tab1 = tabla([r"$\phi_s$ (°)", "Celdas", r"$|\Delta\phi|<60°$", "Energía final", r"$\sigma_\phi$ final (°)", r"$\sigma_W$ final (keV)"], filas,
             r"Estabilidad de un paquete ($\sigma_\phi=15°$, $\sigma_W/W=0{,}5~\%$ iniciales) para distintas fases síncronas; cada fase tiene su propio diseño de celdas. ``Energía final'': fracción que llega a la energía de diseño $\pm1$~MeV.", "estabilidad")
filas = [[pct(ef, 1), pct(f.capturadas, 1), num(f.T_medio_final, 2), num(f.fase_media_final, 1)] for ef, f in ER.iterrows()]
tab2 = tabla(["Error de frecuencia", "Capturadas", r"$\langle T\rangle$ final (MeV)", "Desplazamiento de fase (°)"], filas,
             r"Efecto de un error relativo en la frecuencia del RF ($\phi_s=-30°$).", "errorf")

secciones = [
 ("Introducción", r"""
Un acelerador lineal (linac) acelera partículas haciéndolas atravesar una sucesión de cavidades o huecos en los que un campo
eléctrico de radiofrecuencia las empuja. Para que el campo empuje siempre en el sentido correcto, la partícula debe llegar a
cada hueco en la misma fase del RF: mientras está en los tubos de deriva, apantallada, el campo cambia de signo. Por eso las
celdas deben alargarse a medida que la partícula se acelera. Los linacs son los inyectores de casi todos los grandes
aceleradores, se usan en radioterapia (electrones de 6--18~MeV) y son la base de las fuentes de espalación. Este proyecto
estudia el diseño de un linac de protones, la dinámica longitudinal de un paquete y la estabilidad de fase.
"""),
 ("Objetivos", r"""
\begin{enumerate}
\item Implementar el modelo de aceleración por cavidades $\Delta E=qV\cos\phi$ y $E_N=E_0+\sum qV_i\cos\phi_i$.
\item Diseñar las longitudes de las celdas para la partícula síncrona.
\item Estudiar el efecto de la fase y la sincronización sobre un paquete de partículas.
\item Verificar la teoría de las oscilaciones de sincrotrón y comparar protones con electrones.
\end{enumerate}
"""),
 ("Fundamento físico", rellenar(r"""
En el hueco $i$ la partícula gana $\Delta E_i=qV\cos\phi_i$, donde $\phi_i$ es la fase del RF al cruzarlo ($\phi=0$ en la cresta).
Para que la partícula síncrona llegue a cada hueco con la misma fase $\phi_s$, la distancia entre huecos debe recorrerse en un
periodo del RF: $L_n=\beta_n\lambda$, con $\lambda=c/f=@lam@$~cm (estructura de Alvarez). Una partícula que llega con un pequeño
retraso $\Delta\phi$ recibe una energía distinta; si $\phi_s<0$ (la partícula llega antes de la cresta, en el flanco de subida del
voltaje), la que llega tarde gana \emph{más} energía, va más rápida y se adelanta: la fase es estable. Linealizando,
\begin{equation}
\frac{d\Delta\phi}{dn}=-\frac{2\pi\,\Delta W}{mc^2\beta^2\gamma^3},\qquad \frac{d\Delta W}{dn}=-qV\sin\phi_s\,\Delta\phi, \label{eq:lin}
\end{equation}
que describe oscilaciones (de sincrotrón) con avance de fase por celda
\begin{equation}
\mu^2=\frac{2\pi qV(-\sin\phi_s)}{mc^2\beta^2\gamma^3}. \label{eq:mu}
\end{equation}
Con $\phi_s>0$ la partícula retrasada gana menos energía y se retrasa aún más: inestable. El precio de la estabilidad es una
ganancia menor que la máxima ($\cos\phi_s<1$). Para amplitudes grandes la dinámica es la de un péndulo, con una región estable
(separatriz) que va de $-\phi_s$ a una fase $\phi_2\approx2\phi_s$. Al acelerarse, $\mu$ disminuye y la amplitud de fase se
amortigua adiabáticamente (como $(\beta\gamma)^{-3/4}$).

Los electrones de más de unos MeV ya viajan a $\beta\approx1$: su fase no cambia, no hay oscilaciones y pueden acelerarse en la cresta.
""", v)),
 ("Modelo matemático", rellenar(r"""
Cada partícula se describe por $(T_i,\phi_i)$ a la entrada del hueco $i$. El mapa de una celda es
\begin{align}
T_{i+1}&=T_i+qV\cos\phi_i,\\
\phi_{i+1}&=\phi_i+\omega\frac{L_i}{\beta(T_{i+1})c}-2\pi ,
\end{align}
donde $L_i$ es la celda de diseño. Para la partícula síncrona el segundo término es exactamente $2\pi$ y su fase no cambia. Un
error relativo $\epsilon$ en la frecuencia se modela sustituyendo $\omega$ por $\omega(1+\epsilon)$. Parámetros: $f=@f@$~MHz,
$qV=@qV@$~MeV por hueco, $T$ de @T0@ a @Tf@~MeV.
""", v)),
 ("Método numérico", r"""
El diseño se construye iterando la ecuación de la energía para la partícula síncrona y calculando $\beta$ al final de cada
celda. El mapa se aplica de forma vectorizada a \num{3000} partículas con $\Delta\phi_0\sim\mathcal N(0,15°)$ y
$\Delta T_0/T_0\sim\mathcal N(0;0{,}5~\%)$. El avance de fase simulado se mide a partir de los cruces por cero de $\Delta\phi$ de
una partícula con amplitud inicial de 3° (medio periodo entre cruces consecutivos) y se compara con~\eqref{eq:mu}.
"""),
 ("Implementación computacional", r"""
\texttt{src/modelo.py} contiene $\beta(T)$, el diseño de celdas, el seguimiento del paquete, el avance de fase teórico y la
aceptancia de fase. \texttt{src/simulacion.py} produce el diseño, la tabla de estabilidad, las oscilaciones, el estudio del error
de frecuencia y el caso de los electrones; los paquetes completos se guardan en \texttt{datos/paquete\_fase*.npz}.
"""),
 ("Resultados", rellenar(r"""
\subsection{Diseño}
Con $\phi_s=-30°$ la partícula síncrona gana @gan@~MeV por hueco y necesita @N@ celdas y @Ltot@~m para ir de @T0@ a @Tf@~MeV
(gradiente medio @grad@~MeV/m). Las celdas crecen de @L1@ a @L2@~cm, siguiendo $\beta\lambda$ (figura~\ref{fig:fig01_diseno}).
Con $\phi_s=-60°$ harían falta @N60@ celdas y en la cresta solo @N0@: la estabilidad cuesta longitud.
@fig1@
\subsection{Estabilidad de fase}
La figura~\ref{fig:fig02_espacio_fases} muestra el paquete en el espacio $(\Delta\phi,\Delta W)$. Con $\phi_s=-30°$ las partículas giran
alrededor de la síncrona: la dispersión de fase se reduce de @dphi0@° a @dphi30@° (amortiguamiento adiabático) a cambio de una dispersión
de energía de @dW30@~keV, y el @c30@ permanece agrupado. La tabla~\ref{tab:estabilidad} compara las fases síncronas: con $-60°$ se conserva
el @c60@ y con $-15°$ el @c15@ (la separatriz es más estrecha). En la cresta ($\phi_s=0$) no hay fuerza restauradora y solo el @a0@ del paquete
llega a la energía final. Con $\phi_s=+30°$ el síncrono de diseño es inestable, pero ocurre algo instructivo: parte del paquete migra a la
fase estable simétrica $-30°$, que da la misma ganancia $\cos(\pm30°)$; el @a30p@ llega a la energía final con una fase media de @fm30p@°.
@tab1@
@fig2@
\subsection{Oscilaciones de sincrotrón}
Una partícula con 3° de desfase inicial oscila alrededor de la síncrona (figura~\ref{fig:fig03_sincrotron}). El avance de fase medido en la
primera semioscilación es @musim@°/celda, frente a @muteo@° de la ecuación~\eqref{eq:mu}; a lo largo del linac el avance teórico baja de
@mu0@° a @mu1@° por celda y la simulación lo sigue. La amplitud se reduce de @amp0@° a @amp1@°: es el amortiguamiento adiabático, del orden de la ley
$(\beta\gamma)^{-3/4}$ (que predice un factor 0,35 entre 3 y 50~MeV; el valor simulado, 0,46, incluye la fase de la oscilación en la
última celda).
@fig3@
\subsection{Sincronización y electrones}
Un error en la frecuencia hace que el paquete llegue cada vez a una fase distinta; la estabilidad de fase lo compensa desplazando el
paquete hacia una nueva fase de equilibrio (tabla~\ref{tab:errorf}): con un 1~\% de error el paquete se desplaza @fs1@° y llega a @Te1@~MeV,
conservando el @e1@ de las partículas; con un 2~\% se conserva el @e2@ y con un 4~\% solo el @e4@ (figura~\ref{fig:fig04_estabilidad_electrones}(b)).
Los electrones de @eTi@~MeV inyectados en @nE@ celdas de longitud $\lambda$ alcanzan @eT@~MeV en la cresta, y su fase deriva solo @ed@° en todo el
linac: sin oscilaciones, la energía final depende directamente de la fase de inyección ($\cos40°$: @eT40@~MeV), figura~\ref{fig:fig04_estabilidad_electrones}(c).
@tab2@
@fig4@
""", {**v, "tab1": tab1, "tab2": tab2,
      "fig1": figura("fig01_diseno", r"(a) Energía de la partícula síncrona en cada hueco y (b) longitud de las celdas del linac ($\phi_s=-30°$)."),
      "fig2": figura("fig02_espacio_fases", r"Espacio de fases longitudinal del paquete al principio, en la mitad y al final del linac para $\phi_s=-30°$ (arriba, estable) y $\phi_s=+30°$ (abajo)."),
      "fig3": figura("fig03_sincrotron", r"(a) Oscilación de fase de una partícula con 3° de desfase inicial. (b) Avance de fase por celda: teoría de pequeña amplitud y simulación."),
      "fig4": figura("fig04_estabilidad_electrones", r"(a) Fracción del paquete agrupada y fracción que llega a la energía final frente a la fase síncrona. (b) Efecto de un error de frecuencia. (c) Energía de electrones inyectados con distintas fases.")})),
 ("Análisis de incertidumbre y validación", r"""
\begin{itemize}
\item \textbf{Ecuación de la guía:} la energía del síncrono reproduce exactamente $E_N=E_0+NqV\cos\phi_s$.
\item \textbf{Teoría lineal:} el avance de fase simulado coincide con~\eqref{eq:mu} dentro de la resolución de la medida (que usa un
      número entero de celdas por semioscilación).
\item \textbf{Comportamiento cualitativo:} estabilidad para $\phi_s<0$ e inestabilidad para $\phi_s>0$, como predice la teoría.
\item \textbf{Estadística:} con \num{3000} partículas, las fracciones tienen errores de $\sim1~\%$.
\item \textbf{Simplificaciones:} huecos de longitud nula (sin factor de tiempo de tránsito), voltaje constante en todas las celdas,
      sin dinámica transversal (en un linac real la focalización de fase desenfoca transversalmente y se compensa con cuadrupolos),
      sin carga espacial.
\end{itemize}
"""),
 ("Discusión", r"""
La estabilidad de fase, descubierta por Veksler y McMillan en 1944--45, es la idea que hizo posibles los aceleradores modernos:
basta elegir la fase síncrona en el flanco adecuado del RF para que el paquete se mantenga unido de forma natural, aunque las partículas
tengan energías y fases ligeramente distintas. El mismo principio funciona en los sincrotrones. El proyecto muestra también el compromiso
de diseño: una fase síncrona más negativa da una región estable más grande pero menos ganancia por celda y por tanto un linac más largo.
Para electrones relativistas el problema es distinto: no hay oscilaciones, la fase se fija en la inyección y el agrupamiento se hace antes,
en un ``buncher''. Por eso los linacs médicos de electrones son compactos y trabajan cerca de la cresta.
"""),
 ("Conclusiones", rellenar(r"""
\begin{itemize}
\item Linac de protones de @T0@ a @Tf@~MeV con @qV@~MV por hueco y $\phi_s=-30°$: @N@ celdas, @Ltot@~m, celdas de @L1@ a @L2@~cm.
\item Con $\phi_s=-30°$ el paquete es estable (@c30@ agrupado); en la cresta solo llega a la energía final el @a0@.
\item El avance de fase de las oscilaciones de sincrotrón sigue la teoría lineal y la amplitud se amortigua adiabáticamente.
\item La estabilidad de fase tolera errores de frecuencia de hasta $\sim2~\%$; los electrones no tienen oscilaciones de fase.
\end{itemize}
""", v)),
]
referencias = [
    ("wangler", r"T.~P. Wangler, \emph{RF Linear Accelerators}, 2.ª ed., Wiley-VCH (2008), caps. 4 y 6."),
    ("wille", r"K. Wille, \emph{The Physics of Particle Accelerators}, Oxford University Press (2000), cap. 4."),
    ("veksler", r"V.~I. Veksler, ``A new method of acceleration of relativistic particles'', \emph{J. Phys. USSR} \textbf{9} (1945) 153; E.~M. McMillan, \emph{Phys. Rev.} \textbf{68} (1945) 143."),
    ("cas", r"CERN Accelerator School, \emph{RF for Accelerators}, CERN-2011-007 (2011)."),
]
escribir_informe(P, meta, secciones, referencias)
presentacion(P, meta, [
    dict(titulo="Modelo", items=[r"$\Delta E=qV\cos\phi$; \ $E_N=E_0+\sum qV_i\cos\phi_i$; \ celdas $L_n=\beta_n\lambda$.",
                                 r"Mapa por celda: $T_{i+1}=T_i+qV\cos\phi_i$, \ $\phi_{i+1}=\phi_i+\omega L_i/(\beta c)-2\pi$.",
                                 r"Estabilidad para $\phi_s<0$: $\mu^2=2\pi qV(-\sin\phi_s)/(mc^2\beta^2\gamma^3)$."]),
    dict(titulo="Diseño de las celdas", figura="fig01_diseno"),
    dict(titulo="Espacio de fases", figura="fig02_espacio_fases"),
    dict(titulo="Oscilaciones de sincrotrón", figura="fig03_sincrotron"),
    dict(titulo="Fase, sincronización y electrones", figura="fig04_estabilidad_electrones"),
    dict(titulo="Conclusiones", items=[rellenar(r"@T0@ $\to$ @Tf@~MeV: @N@ celdas, @Ltot@~m.", v),
                                       rellenar(r"$\phi_s=-30°$: @c30@ agrupado; cresta: @a0@.", v), "Electrones: sin oscilaciones de fase."]),
])
escribir_readme(P, meta, "Linac de protones de tubos de deriva: diseño de celdas βλ, dinámica longitudinal de un paquete, estabilidad de fase, oscilaciones de sincrotrón, error de frecuencia y electrones.",
                f"""- 3 → 50 MeV, qV = 1 MeV, φs = −30°: {d['celdas']} celdas, {d['longitud_m']:.2f} m (celdas de {100*d['L_primera']:.1f} a {100*d['L_ultima']:.1f} cm).
- Paquete agrupado: {100*EST.loc[-60,'capturadas']:.1f} % (−60°), {100*EST.loc[-30,'capturadas']:.1f} % (−30°); en la cresta solo {100*EST.loc[0,'aceleradas']:.1f} % llega a la energía final.
- Avance de fase de sincrotrón: {np.degrees(MU.mu_sim.iloc[0]):.1f}°/celda simulado frente a {np.degrees(MU.mu_teo.iloc[0]):.1f}° teórico.
- Electrones (β≈1): sin oscilaciones; energía final ∝ cos φ de inyección.""")
