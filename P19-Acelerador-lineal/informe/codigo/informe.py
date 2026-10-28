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
$\Delta E=qV\cos\phi$, de modo que tras $N$ cavidades $E_N=E_0+\sum qV_i\cos\phi_i$. Se dise(*@\~n@*)an las celdas para la part(*@\'{\i}@*)cula
s(*@\'{\i}@*)ncrona ($L_n=\beta_n\lambda$): con $qV=@qV@$~MeV y $\phi_s=-30(*@$^\circ$@*)$ se pasa de @T0@ a @Tf@~MeV en @N@ celdas y @Ltot@~m. Siguiendo un
paquete de \num{3000} part(*@\'{\i}@*)culas con dispersi(*@\'o@*)n de fase y energ(*@\'{\i}@*)a se estudia la estabilidad de fase: con $\phi_s=-30(*@$^\circ$@*)$ el @c30@ del
paquete permanece agrupado y realiza oscilaciones de sincrotr(*@\'o@*)n cuyo avance de fase coincide con la teor(*@\'{\i}@*)a de peque(*@\~n@*)a amplitud,
mientras que en la cresta ($\phi_s=0$) solo el @a0@ llega a la energ(*@\'{\i}@*)a final. Se estudian adem(*@\'a@*)s el efecto de un error en la
frecuencia del RF y el caso de los electrones, que viajan a $\beta\simeq1$ y no tienen oscilaciones de fase.""", v)

filas = [[f"{ps:+d}" if ps else "0", str(int(f.celdas)), pct(f.capturadas, 1), pct(f.aceleradas, 1), num(f.dphi_rms_final, 1), num(1000 * f.dW_rms_final_MeV, 0)]
         for ps, f in EST.iterrows()]
tab1 = tabla([r"$\phi_s$ ((*@$^\circ$@*))", "Celdas", r"$|\Delta\phi|<60(*@$^\circ$@*)$", "Energ(*@\'{\i}@*)a final", r"$\sigma_\phi$ final ((*@$^\circ$@*))", r"$\sigma_W$ final (keV)"], filas,
             r"Estabilidad de un paquete ($\sigma_\phi=15(*@$^\circ$@*)$, $\sigma_W/W=0{,}5~\%$ iniciales) para distintas fases s(*@\'{\i}@*)ncronas; cada fase tiene su propio dise(*@\~n@*)o de celdas. ``Energ(*@\'{\i}@*)a final'': fracci(*@\'o@*)n que llega a la energ(*@\'{\i}@*)a de dise(*@\~n@*)o $\pm1$~MeV.", "estabilidad")
filas = [[pct(ef, 1), pct(f.capturadas, 1), num(f.T_medio_final, 2), num(f.fase_media_final, 1)] for ef, f in ER.iterrows()]
tab2 = tabla(["Error de frecuencia", "Capturadas", r"$\langle T\rangle$ final (MeV)", "Desplazamiento de fase ((*@$^\circ$@*))"], filas,
             r"Efecto de un error relativo en la frecuencia del RF ($\phi_s=-30(*@$^\circ$@*)$).", "errorf")

secciones = [
 ("Introducci(*@\'o@*)n", r"""
Un acelerador lineal (linac) acelera part(*@\'{\i}@*)culas haci(*@\'e@*)ndolas atravesar una sucesi(*@\'o@*)n de cavidades o huecos en los que un campo
el(*@\'e@*)ctrico de radiofrecuencia las empuja. Para que el campo empuje siempre en el sentido correcto, la part(*@\'{\i}@*)cula debe llegar a
cada hueco en la misma fase del RF: mientras est(*@\'a@*) en los tubos de deriva, apantallada, el campo cambia de signo. Por eso las
celdas deben alargarse a medida que la part(*@\'{\i}@*)cula se acelera. Los linacs son los inyectores de casi todos los grandes
aceleradores, se usan en radioterapia (electrones de 6--18~MeV) y son la base de las fuentes de espalaci(*@\'o@*)n. Este proyecto
estudia el dise(*@\~n@*)o de un linac de protones, la din(*@\'a@*)mica longitudinal de un paquete y la estabilidad de fase.
"""),
 ("Objetivos", r"""
\begin{enumerate}
\item Implementar el modelo de aceleraci(*@\'o@*)n por cavidades $\Delta E=qV\cos\phi$ y $E_N=E_0+\sum qV_i\cos\phi_i$.
\item Dise(*@\~n@*)ar las longitudes de las celdas para la part(*@\'{\i}@*)cula s(*@\'{\i}@*)ncrona.
\item Estudiar el efecto de la fase y la sincronizaci(*@\'o@*)n sobre un paquete de part(*@\'{\i}@*)culas.
\item Verificar la teor(*@\'{\i}@*)a de las oscilaciones de sincrotr(*@\'o@*)n y comparar protones con electrones.
\end{enumerate}
"""),
 ("Fundamento f(*@\'{\i}@*)sico", rellenar(r"""
En el hueco $i$ la part(*@\'{\i}@*)cula gana $\Delta E_i=qV\cos\phi_i$, donde $\phi_i$ es la fase del RF al cruzarlo ($\phi=0$ en la cresta).
Para que la part(*@\'{\i}@*)cula s(*@\'{\i}@*)ncrona llegue a cada hueco con la misma fase $\phi_s$, la distancia entre huecos debe recorrerse en un
periodo del RF: $L_n=\beta_n\lambda$, con $\lambda=c/f=@lam@$~cm (estructura de Alvarez). Una part(*@\'{\i}@*)cula que llega con un peque(*@\~n@*)o
retraso $\Delta\phi$ recibe una energ(*@\'{\i}@*)a distinta; si $\phi_s<0$ (la part(*@\'{\i}@*)cula llega antes de la cresta, en el flanco de subida del
voltaje), la que llega tarde gana \emph{m(*@\'a@*)s} energ(*@\'{\i}@*)a, va m(*@\'a@*)s r(*@\'a@*)pida y se adelanta: la fase es estable. Linealizando,
\begin{equation}
\frac{d\Delta\phi}{dn}=-\frac{2\pi\,\Delta W}{mc^2\beta^2\gamma^3},\qquad \frac{d\Delta W}{dn}=-qV\sin\phi_s\,\Delta\phi, \label{eq:lin}
\end{equation}
que describe oscilaciones (de sincrotr(*@\'o@*)n) con avance de fase por celda
\begin{equation}
\mu^2=\frac{2\pi qV(-\sin\phi_s)}{mc^2\beta^2\gamma^3}. \label{eq:mu}
\end{equation}
Con $\phi_s>0$ la part(*@\'{\i}@*)cula retrasada gana menos energ(*@\'{\i}@*)a y se retrasa a(*@\'u@*)n m(*@\'a@*)s: inestable. El precio de la estabilidad es una
ganancia menor que la m(*@\'a@*)xima ($\cos\phi_s<1$). Para amplitudes grandes la din(*@\'a@*)mica es la de un p(*@\'e@*)ndulo, con una regi(*@\'o@*)n estable
(separatriz) que va de $-\phi_s$ a una fase $\phi_2\approx2\phi_s$. Al acelerarse, $\mu$ disminuye y la amplitud de fase se
amortigua adiab(*@\'a@*)ticamente (como $(\beta\gamma)^{-3/4}$).

Los electrones de m(*@\'a@*)s de unos MeV ya viajan a $\beta\approx1$: su fase no cambia, no hay oscilaciones y pueden acelerarse en la cresta.
""", v)),
 ("Modelo matem(*@\'a@*)tico", rellenar(r"""
Cada part(*@\'{\i}@*)cula se describe por $(T_i,\phi_i)$ a la entrada del hueco $i$. El mapa de una celda es
\begin{align}
T_{i+1}&=T_i+qV\cos\phi_i,\\
\phi_{i+1}&=\phi_i+\omega\frac{L_i}{\beta(T_{i+1})c}-2\pi ,
\end{align}
donde $L_i$ es la celda de dise(*@\~n@*)o. Para la part(*@\'{\i}@*)cula s(*@\'{\i}@*)ncrona el segundo t(*@\'e@*)rmino es exactamente $2\pi$ y su fase no cambia. Un
error relativo $\epsilon$ en la frecuencia se modela sustituyendo $\omega$ por $\omega(1+\epsilon)$. Par(*@\'a@*)metros: $f=@f@$~MHz,
$qV=@qV@$~MeV por hueco, $T$ de @T0@ a @Tf@~MeV.
""", v)),
 ("M(*@\'e@*)todo num(*@\'e@*)rico", r"""
El dise(*@\~n@*)o se construye iterando la ecuaci(*@\'o@*)n de la energ(*@\'{\i}@*)a para la part(*@\'{\i}@*)cula s(*@\'{\i}@*)ncrona y calculando $\beta$ al final de cada
celda. El mapa se aplica de forma vectorizada a \num{3000} part(*@\'{\i}@*)culas con $\Delta\phi_0\sim\mathcal N(0,15(*@$^\circ$@*))$ y
$\Delta T_0/T_0\sim\mathcal N(0;0{,}5~\%)$. El avance de fase simulado se mide a partir de los cruces por cero de $\Delta\phi$ de
una part(*@\'{\i}@*)cula con amplitud inicial de 3(*@$^\circ$@*) (medio periodo entre cruces consecutivos) y se compara con~\eqref{eq:mu}.
"""),
 ("Implementaci(*@\'o@*)n computacional", r"""
\texttt{src/modelo.py} contiene $\beta(T)$, el dise(*@\~n@*)o de celdas, el seguimiento del paquete, el avance de fase te(*@\'o@*)rico y la
aceptancia de fase. \texttt{src/simulacion.py} produce el dise(*@\~n@*)o, la tabla de estabilidad, las oscilaciones, el estudio del error
de frecuencia y el caso de los electrones; los paquetes completos se guardan en \texttt{datos/paquete\_fase*.npz}.
"""),
 ("Resultados", rellenar(r"""
\subsection{Dise(*@\~n@*)o}
Con $\phi_s=-30(*@$^\circ$@*)$ la part(*@\'{\i}@*)cula s(*@\'{\i}@*)ncrona gana @gan@~MeV por hueco y necesita @N@ celdas y @Ltot@~m para ir de @T0@ a @Tf@~MeV
(gradiente medio @grad@~MeV/m). Las celdas crecen de @L1@ a @L2@~cm, siguiendo $\beta\lambda$ (figura~\ref{fig:fig01_diseno}).
Con $\phi_s=-60(*@$^\circ$@*)$ har(*@\'{\i}@*)an falta @N60@ celdas y en la cresta solo @N0@: la estabilidad cuesta longitud.
@fig1@
\subsection{Estabilidad de fase}
La figura~\ref{fig:fig02_espacio_fases} muestra el paquete en el espacio $(\Delta\phi,\Delta W)$. Con $\phi_s=-30(*@$^\circ$@*)$ las part(*@\'{\i}@*)culas giran
alrededor de la s(*@\'{\i}@*)ncrona: la dispersi(*@\'o@*)n de fase se reduce de @dphi0@(*@$^\circ$@*) a @dphi30@(*@$^\circ$@*) (amortiguamiento adiab(*@\'a@*)tico) a cambio de una dispersi(*@\'o@*)n
de energ(*@\'{\i}@*)a de @dW30@~keV, y el @c30@ permanece agrupado. La tabla~\ref{tab:estabilidad} compara las fases s(*@\'{\i}@*)ncronas: con $-60(*@$^\circ$@*)$ se conserva
el @c60@ y con $-15(*@$^\circ$@*)$ el @c15@ (la separatriz es m(*@\'a@*)s estrecha). En la cresta ($\phi_s=0$) no hay fuerza restauradora y solo el @a0@ del paquete
llega a la energ(*@\'{\i}@*)a final. Con $\phi_s=+30(*@$^\circ$@*)$ el s(*@\'{\i}@*)ncrono de dise(*@\~n@*)o es inestable, pero ocurre algo instructivo: parte del paquete migra a la
fase estable sim(*@\'e@*)trica $-30(*@$^\circ$@*)$, que da la misma ganancia $\cos(\pm30(*@$^\circ$@*))$; el @a30p@ llega a la energ(*@\'{\i}@*)a final con una fase media de @fm30p@(*@$^\circ$@*).
@tab1@
@fig2@
\subsection{Oscilaciones de sincrotr(*@\'o@*)n}
Una part(*@\'{\i}@*)cula con 3(*@$^\circ$@*) de desfase inicial oscila alrededor de la s(*@\'{\i}@*)ncrona (figura~\ref{fig:fig03_sincrotron}). El avance de fase medido en la
primera semioscilaci(*@\'o@*)n es @musim@(*@$^\circ$@*)/celda, frente a @muteo@(*@$^\circ$@*) de la ecuaci(*@\'o@*)n~\eqref{eq:mu}; a lo largo del linac el avance te(*@\'o@*)rico baja de
@mu0@(*@$^\circ$@*) a @mu1@(*@$^\circ$@*) por celda y la simulaci(*@\'o@*)n lo sigue. La amplitud se reduce de @amp0@(*@$^\circ$@*) a @amp1@(*@$^\circ$@*): es el amortiguamiento adiab(*@\'a@*)tico, del orden de la ley
$(\beta\gamma)^{-3/4}$ (que predice un factor 0,35 entre 3 y 50~MeV; el valor simulado, 0,46, incluye la fase de la oscilaci(*@\'o@*)n en la
(*@\'u@*)ltima celda).
@fig3@
\subsection{Sincronizaci(*@\'o@*)n y electrones}
Un error en la frecuencia hace que el paquete llegue cada vez a una fase distinta; la estabilidad de fase lo compensa desplazando el
paquete hacia una nueva fase de equilibrio (tabla~\ref{tab:errorf}): con un 1~\% de error el paquete se desplaza @fs1@(*@$^\circ$@*) y llega a @Te1@~MeV,
conservando el @e1@ de las part(*@\'{\i}@*)culas; con un 2~\% se conserva el @e2@ y con un 4~\% solo el @e4@ (figura~\ref{fig:fig04_estabilidad_electrones}(b)).
Los electrones de @eTi@~MeV inyectados en @nE@ celdas de longitud $\lambda$ alcanzan @eT@~MeV en la cresta, y su fase deriva solo @ed@(*@$^\circ$@*) en todo el
linac: sin oscilaciones, la energ(*@\'{\i}@*)a final depende directamente de la fase de inyecci(*@\'o@*)n ($\cos40(*@$^\circ$@*)$: @eT40@~MeV), figura~\ref{fig:fig04_estabilidad_electrones}(c).
@tab2@
@fig4@
""", {**v, "tab1": tab1, "tab2": tab2,
      "fig1": figura("fig01_diseno", r"(a) Energ(*@\'{\i}@*)a de la part(*@\'{\i}@*)cula s(*@\'{\i}@*)ncrona en cada hueco y (b) longitud de las celdas del linac ($\phi_s=-30(*@$^\circ$@*)$)."),
      "fig2": figura("fig02_espacio_fases", r"Espacio de fases longitudinal del paquete al principio, en la mitad y al final del linac para $\phi_s=-30(*@$^\circ$@*)$ (arriba, estable) y $\phi_s=+30(*@$^\circ$@*)$ (abajo)."),
      "fig3": figura("fig03_sincrotron", r"(a) Oscilaci(*@\'o@*)n de fase de una part(*@\'{\i}@*)cula con 3(*@$^\circ$@*) de desfase inicial. (b) Avance de fase por celda: teor(*@\'{\i}@*)a de peque(*@\~n@*)a amplitud y simulaci(*@\'o@*)n."),
      "fig4": figura("fig04_estabilidad_electrones", r"(a) Fracci(*@\'o@*)n del paquete agrupada y fracci(*@\'o@*)n que llega a la energ(*@\'{\i}@*)a final frente a la fase s(*@\'{\i}@*)ncrona. (b) Efecto de un error de frecuencia. (c) Energ(*@\'{\i}@*)a de electrones inyectados con distintas fases.")})),
 ("An(*@\'a@*)lisis de incertidumbre y validaci(*@\'o@*)n", r"""
\begin{itemize}
\item \textbf{Ecuaci(*@\'o@*)n de la gu(*@\'{\i}@*)a:} la energ(*@\'{\i}@*)a del s(*@\'{\i}@*)ncrono reproduce exactamente $E_N=E_0+NqV\cos\phi_s$.
\item \textbf{Teor(*@\'{\i}@*)a lineal:} el avance de fase simulado coincide con~\eqref{eq:mu} dentro de la resoluci(*@\'o@*)n de la medida (que usa un
      n(*@\'u@*)mero entero de celdas por semioscilaci(*@\'o@*)n).
\item \textbf{Comportamiento cualitativo:} estabilidad para $\phi_s<0$ e inestabilidad para $\phi_s>0$, como predice la teor(*@\'{\i}@*)a.
\item \textbf{Estad(*@\'{\i}@*)stica:} con \num{3000} part(*@\'{\i}@*)culas, las fracciones tienen errores de $\sim1~\%$.
\item \textbf{Simplificaciones:} huecos de longitud nula (sin factor de tiempo de tr(*@\'a@*)nsito), voltaje constante en todas las celdas,
      sin din(*@\'a@*)mica transversal (en un linac real la focalizaci(*@\'o@*)n de fase desenfoca transversalmente y se compensa con cuadrupolos),
      sin carga espacial.
\end{itemize}
"""),
 ("Discusi(*@\'o@*)n", r"""
La estabilidad de fase, descubierta por Veksler y McMillan en 1944--45, es la idea que hizo posibles los aceleradores modernos:
basta elegir la fase s(*@\'{\i}@*)ncrona en el flanco adecuado del RF para que el paquete se mantenga unido de forma natural, aunque las part(*@\'{\i}@*)culas
tengan energ(*@\'{\i}@*)as y fases ligeramente distintas. El mismo principio funciona en los sincrotrones. El proyecto muestra tambi(*@\'e@*)n el compromiso
de dise(*@\~n@*)o: una fase s(*@\'{\i}@*)ncrona m(*@\'a@*)s negativa da una regi(*@\'o@*)n estable m(*@\'a@*)s grande pero menos ganancia por celda y por tanto un linac m(*@\'a@*)s largo.
Para electrones relativistas el problema es distinto: no hay oscilaciones, la fase se fija en la inyecci(*@\'o@*)n y el agrupamiento se hace antes,
en un ``buncher''. Por eso los linacs m(*@\'e@*)dicos de electrones son compactos y trabajan cerca de la cresta.
"""),
 ("Conclusiones", rellenar(r"""
\begin{itemize}
\item Linac de protones de @T0@ a @Tf@~MeV con @qV@~MV por hueco y $\phi_s=-30(*@$^\circ$@*)$: @N@ celdas, @Ltot@~m, celdas de @L1@ a @L2@~cm.
\item Con $\phi_s=-30(*@$^\circ$@*)$ el paquete es estable (@c30@ agrupado); en la cresta solo llega a la energ(*@\'{\i}@*)a final el @a0@.
\item El avance de fase de las oscilaciones de sincrotr(*@\'o@*)n sigue la teor(*@\'{\i}@*)a lineal y la amplitud se amortigua adiab(*@\'a@*)ticamente.
\item La estabilidad de fase tolera errores de frecuencia de hasta $\sim2~\%$; los electrones no tienen oscilaciones de fase.
\end{itemize}
""", v)),
]
referencias = [
    ("wangler", r"T.~P. Wangler, \emph{RF Linear Accelerators}, 2.(*@?@*) ed., Wiley-VCH (2008), caps. 4 y 6."),
    ("wille", r"K. Wille, \emph{The Physics of Particle Accelerators}, Oxford University Press (2000), cap. 4."),
    ("veksler", r"V.~I. Veksler, ``A new method of acceleration of relativistic particles'', \emph{J. Phys. USSR} \textbf{9} (1945) 153; E.~M. McMillan, \emph{Phys. Rev.} \textbf{68} (1945) 143."),
    ("cas", r"CERN Accelerator School, \emph{RF for Accelerators}, CERN-2011-007 (2011)."),
]
escribir_informe(P, meta, secciones, referencias)
presentacion(P, meta, [
    dict(titulo="Modelo", items=[r"$\Delta E=qV\cos\phi$; \ $E_N=E_0+\sum qV_i\cos\phi_i$; \ celdas $L_n=\beta_n\lambda$.",
                                 r"Mapa por celda: $T_{i+1}=T_i+qV\cos\phi_i$, \ $\phi_{i+1}=\phi_i+\omega L_i/(\beta c)-2\pi$.",
                                 r"Estabilidad para $\phi_s<0$: $\mu^2=2\pi qV(-\sin\phi_s)/(mc^2\beta^2\gamma^3)$."]),
    dict(titulo="Dise(*@\~n@*)o de las celdas", figura="fig01_diseno"),
    dict(titulo="Espacio de fases", figura="fig02_espacio_fases"),
    dict(titulo="Oscilaciones de sincrotr(*@\'o@*)n", figura="fig03_sincrotron"),
    dict(titulo="Fase, sincronizaci(*@\'o@*)n y electrones", figura="fig04_estabilidad_electrones"),
    dict(titulo="Conclusiones", items=[rellenar(r"@T0@ $\to$ @Tf@~MeV: @N@ celdas, @Ltot@~m.", v),
                                       rellenar(r"$\phi_s=-30(*@$^\circ$@*)$: @c30@ agrupado; cresta: @a0@.", v), "Electrones: sin oscilaciones de fase."]),
])
escribir_readme(P, meta, "Linac de protones de tubos de deriva: dise(*@\~n@*)o de celdas (*@$\beta$@*)(*@$\lambda$@*), din(*@\'a@*)mica longitudinal de un paquete, estabilidad de fase, oscilaciones de sincrotr(*@\'o@*)n, error de frecuencia y electrones.",
                f"""- 3 (*@$\to$@*) 50 MeV, qV = 1 MeV, (*@$\phi$@*)s = (*@-@*)30(*@$^\circ$@*): {d['celdas']} celdas, {d['longitud_m']:.2f} m (celdas de {100*d['L_primera']:.1f} a {100*d['L_ultima']:.1f} cm).
- Paquete agrupado: {100*EST.loc[-60,'capturadas']:.1f} % ((*@-@*)60(*@$^\circ$@*)), {100*EST.loc[-30,'capturadas']:.1f} % ((*@-@*)30(*@$^\circ$@*)); en la cresta solo {100*EST.loc[0,'aceleradas']:.1f} % llega a la energ(*@\'{\i}@*)a final.
- Avance de fase de sincrotr(*@\'o@*)n: {np.degrees(MU.mu_sim.iloc[0]):.1f}(*@$^\circ$@*)/celda simulado frente a {np.degrees(MU.mu_teo.iloc[0]):.1f}(*@$^\circ$@*) te(*@\'o@*)rico.
- Electrones ((*@$\beta$@*)(*@$\approx$@*)1): sin oscilaciones; energ(*@\'{\i}@*)a final (*@$\propto$@*) cos (*@$\phi$@*) de inyecci(*@\'o@*)n.""")
