"""Generacion de los informes cientificos (LaTeX -> PDF), de las presentaciones (beamer) y del README de cada proyecto.

El texto de cada informe se escribe en LaTeX normal con marcadores @clave@ que se sustituyen por los valores
calculados (funcion rellenar); asi no hay que duplicar llaves como en los f-strings de Python."""
import re
import shutil
import subprocess
from pathlib import Path

AUTOR = "Jaime A. Betancourt"
CURSO = "Herramientas Computacionales para la Física --- Proyectos avanzados con Python"

PREAMBULO = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[spanish,es-tabla,es-nodecimaldot,es-noquoting]{babel}
\spanishplainpercent
\usepackage[a4paper,margin=2.4cm]{geometry}
\usepackage{amsmath,amssymb,graphicx,booktabs,float,xcolor,caption,listings,array}
\usepackage[output-decimal-marker={,},group-separator={\,},group-minimum-digits=4,
            exponent-product=\times,separate-uncertainty=true,range-phrase={--}]{siunitx}
\usepackage[hidelinks]{hyperref}
\DeclareUnicodeCharacter{2080}{\ensuremath{_0}}\DeclareUnicodeCharacter{2081}{\ensuremath{_1}}
\DeclareUnicodeCharacter{2082}{\ensuremath{_2}}\DeclareUnicodeCharacter{2083}{\ensuremath{_3}}
\DeclareUnicodeCharacter{2070}{\ensuremath{^0}}\DeclareUnicodeCharacter{00B9}{\ensuremath{^1}}
\DeclareUnicodeCharacter{2074}{\ensuremath{^4}}\DeclareUnicodeCharacter{2075}{\ensuremath{^5}}
\DeclareUnicodeCharacter{2076}{\ensuremath{^6}}\DeclareUnicodeCharacter{207B}{\ensuremath{^-}}
\DeclareUnicodeCharacter{03B1}{\ensuremath{\alpha}}\DeclareUnicodeCharacter{03B2}{\ensuremath{\beta}}
\DeclareUnicodeCharacter{03B3}{\ensuremath{\gamma}}\DeclareUnicodeCharacter{03B4}{\ensuremath{\delta}}
\DeclareUnicodeCharacter{03B5}{\ensuremath{\varepsilon}}\DeclareUnicodeCharacter{03B8}{\ensuremath{\theta}}
\DeclareUnicodeCharacter{03BB}{\ensuremath{\lambda}}\DeclareUnicodeCharacter{03BC}{\ensuremath{\mu}}
\DeclareUnicodeCharacter{03BD}{\ensuremath{\nu}}\DeclareUnicodeCharacter{03C0}{\ensuremath{\pi}}
\DeclareUnicodeCharacter{03C1}{\ensuremath{\rho}}\DeclareUnicodeCharacter{03C3}{\ensuremath{\sigma}}
\DeclareUnicodeCharacter{03C4}{\ensuremath{\tau}}\DeclareUnicodeCharacter{03C6}{\ensuremath{\phi}}
\DeclareUnicodeCharacter{03C7}{\ensuremath{\chi}}\DeclareUnicodeCharacter{03C9}{\ensuremath{\omega}}
\DeclareUnicodeCharacter{0394}{\ensuremath{\Delta}}\DeclareUnicodeCharacter{03A3}{\ensuremath{\Sigma}}
\DeclareUnicodeCharacter{2212}{\ensuremath{-}}\DeclareUnicodeCharacter{2248}{\ensuremath{\approx}}
\DeclareUnicodeCharacter{2264}{\ensuremath{\le}}\DeclareUnicodeCharacter{2265}{\ensuremath{\ge}}
\DeclareUnicodeCharacter{2192}{\ensuremath{\to}}\DeclareUnicodeCharacter{27E8}{\ensuremath{\langle}}
\DeclareUnicodeCharacter{27E9}{\ensuremath{\rangle}}\DeclareUnicodeCharacter{2032}{\ensuremath{'}}
\DeclareUnicodeCharacter{2033}{\ensuremath{''}}
\captionsetup{font=small,labelfont=bf}
\setlength{\parskip}{4pt}
\definecolor{fondo}{HTML}{F6F6F4}
\lstset{language=Python,basicstyle=\ttfamily\scriptsize,backgroundcolor=\color{fondo},frame=single,
  rulecolor=\color{gray!40},breaklines=true,columns=fullflexible,keepspaces=true,showstringspaces=false,
  numbers=left,numberstyle=\tiny\color{gray},keywordstyle=\color{blue!60!black}\bfseries,
  commentstyle=\color{green!40!black}\itshape,stringstyle=\color{red!50!black},
  escapeinside={(*@}{@*)}}
"""


# ----------------------------------------------------------------------------------------- formato de numeros
def num(x, d=2):
    """numero con d decimales, con coma decimal (siunitx)"""
    return rf"\num{{{x:.{d}f}}}"


def sci(x, c=3):
    """numero en notacion cientifica con c cifras significativas"""
    return rf"\num{{{x:.{c - 1}e}}}"


def sig(x, c=3):
    """numero con c cifras significativas, en notacion normal si es razonable"""
    if x == 0:
        return r"\num{0}"
    import math
    e = math.floor(math.log10(abs(x)))
    if -3 <= e < 6:
        d = max(c - 1 - e, 0)
        return rf"\num{{{x:.{d}f}}}"
    return sci(x, c)


def pm(x, s, d=2):
    """valor +- incertidumbre con d decimales"""
    return rf"\num{{{x:.{d}f} \pm {s:.{d}f}}}"


def pct(x, d=1):
    """fraccion (0-1) expresada en porcentaje"""
    return rf"\num{{{100 * x:.{d}f}}}\,\%"


def rellenar(texto, valores):
    """sustituye @clave@ por valores[clave]; falla si queda algun marcador sin valor"""
    for k, v in valores.items():
        texto = texto.replace(f"@{k}@", str(v))
    resto = re.findall(r"@[A-Za-z_0-9]+@", texto)
    if resto:
        raise KeyError(f"marcadores sin valor: {sorted(set(resto))}")
    return texto


# ----------------------------------------------------------------------------------------- bloques LaTeX
def figura(nombre, pie, ancho=0.95):
    return (rf"""
\begin{{figure}}[H]
\centering
\includegraphics[width={ancho}\linewidth]{{../figuras/{nombre}.pdf}}
\caption{{{pie}}}
\label{{fig:{nombre}}}
\end{{figure}}
""")


def tabla(encabezado, filas, pie, etiqueta, alineacion=None, pequena=True):
    """tabla booktabs; encabezado y filas son listas de cadenas (ya en LaTeX)"""
    al = alineacion or ("l" + "c" * (len(encabezado) - 1))
    esc = lambda c: re.sub(r"(?<!\\)%", r"\\%", str(c))          # % sin escapar (p. ej. en nombres de medios)
    cuerpo = "\n".join(" & ".join(esc(c) for c in f) + r" \\" for f in filas)
    return (rf"""
\begin{{table}}[H]
\centering
\caption{{{pie}}}
\label{{tab:{etiqueta}}}
{r"\small" if pequena else ""}
\begin{{tabular}}{{{al}}}
\toprule
{" & ".join(encabezado)} \\
\midrule
{cuerpo}
\bottomrule
\end{{tabular}}
\end{{table}}
""")


def _arbol(P):
    """lista de archivos del proyecto (para la seccion de reproducibilidad)"""
    filas = []
    for d in ("datos", "src", "resultados", "figuras"):
        for f in sorted((P.raiz / d).glob("*")):
            if f.is_file() and f.suffix != ".pyc":
                t = f.stat().st_size
                tam = f"{t / 1e6:.1f} MB" if t > 1e6 else f"{t / 1e3:.1f} kB"
                filas.append((f"{d}/{f.name}", tam))
    return filas


def _seccion_reproducibilidad(P):
    filas = _arbol(P)
    lineas = "\n".join(rf"\texttt{{{a.replace('_', chr(92) + '_')}}} & {t} \\" for a, t in filas)
    return (r"""
\section{Reproducibilidad y archivos}
Todos los resultados de este informe se regeneran desde la carpeta del proyecto con
\begin{verbatim}
python3 src/simulacion.py     # genera los datos (datos/) y el analisis (resultados/)
python3 src/graficas.py       # genera las figuras (figuras/, PNG y PDF)
python3 src/informe.py        # escribe y compila este informe y la presentacion
\end{verbatim}
Las semillas de los generadores aleatorios están fijadas en \texttt{datos/parametros.json}, de modo que
la ejecución repetida produce exactamente los mismos números. Archivos del proyecto:
{\small
\begin{longtable}{ll}
\toprule
Archivo & Tamaño \\
\midrule
""" + lineas + r"""
\bottomrule
\end{longtable}}
""")


def escribir_informe(P, meta, secciones, referencias, compilar=True):
    """meta: numero, titulo, area, nivel, resumen. secciones: lista (titulo, cuerpo LaTeX).
    referencias: lista (clave, texto). Agrega reproducibilidad y el codigo fuente como apendice."""
    tex = [PREAMBULO, r"\usepackage{longtable}",
           rf"\title{{\textbf{{Proyecto {meta['numero']}. {meta['titulo']}}}\\[4pt]\large {meta['area']} --- Nivel {meta['nivel']}}}",
           rf"\author{{{AUTOR}\\\small {CURSO}}}", r"\date{\today}", r"\begin{document}", r"\maketitle",
           r"\begin{abstract}", meta["resumen"], r"\end{abstract}", r"\tableofcontents", r"\newpage"]
    for tit, cuerpo in secciones:
        tex += [rf"\section{{{tit}}}", cuerpo]
    tex.append(_seccion_reproducibilidad(P))
    tex.append(r"\begin{thebibliography}{99}")
    tex += [rf"\bibitem{{{k}}} {t}" for k, t in referencias]
    tex.append(r"\end{thebibliography}")
    tex += [r"\appendix", r"\section{Código fuente}\label{sec:codigo}",
            "A continuación se incluye el código completo del proyecto. Los módulos comunes "
            r"(\texttt{comun/}) se documentan en el README general de la carpeta \texttt{Computacion-fisica}."]
    for f in sorted(P.src.glob("*.py")):
        tex.append(rf"\subsection*{{\texttt{{src/{f.name.replace('_', chr(92) + '_')}}}}}"
                   rf"\addcontentsline{{toc}}{{subsection}}{{\texttt{{src/{f.name.replace('_', chr(92) + '_')}}}}}")
        tex.append(rf"\lstinputlisting{{codigo/{f.name}}}")
    _codigo_latex(P)
    tex.append(r"\end{document}")
    salida = P.informe / "informe.tex"
    salida.write_text("\n".join(tex))
    print("  informe", salida.name)
    if compilar:
        compilar_tex(salida)


UNICODE_LATEX = {
    "á": r"\'a", "é": r"\'e", "í": r"\'{\i}", "ó": r"\'o", "ú": r"\'u", "ñ": r"\~n", "ü": r'\"u',
    "Á": r"\'A", "É": r"\'E", "Í": r"\'I", "Ó": r"\'O", "Ú": r"\'U", "Ñ": r"\~N", "¿": r"?`", "¡": r"!`",
    "α": r"$\alpha$", "β": r"$\beta$", "γ": r"$\gamma$", "δ": r"$\delta$", "ε": r"$\varepsilon$", "η": r"$\eta$",
    "θ": r"$\theta$", "λ": r"$\lambda$", "μ": r"$\mu$", "µ": r"$\mu$", "ν": r"$\nu$", "ξ": r"$\xi$", "π": r"$\pi$",
    "ρ": r"$\rho$", "σ": r"$\sigma$", "τ": r"$\tau$", "φ": r"$\phi$", "χ": r"$\chi$", "ψ": r"$\psi$",
    "ω": r"$\omega$", "Δ": r"$\Delta$", "Σ": r"$\Sigma$", "Φ": r"$\Phi$", "Ω": r"$\Omega$", "Γ": r"$\Gamma$",
    "Λ": r"$\Lambda$", "Θ": r"$\Theta$",
    "⟨": r"$\langle$", "⟩": r"$\rangle$", "²": r"$^2$", "³": r"$^3$", "¹": r"$^1$", "⁻": r"$^-$", "⁰": r"$^0$",
    "⁴": r"$^4$", "⁵": r"$^5$", "⁶": r"$^6$", "₀": r"$_0$", "₁": r"$_1$", "₂": r"$_2$", "ₑ": r"$_e$",
    "±": r"$\pm$", "×": r"$\times$", "·": r"$\cdot$", "°": r"$^\circ$", "≈": r"$\approx$", "≤": r"$\le$",
    "≥": r"$\ge$", "→": r"$\to$", "∝": r"$\propto$", "−": r"-", "–": r"--", "—": r"---", "“": r"``", "”": r"''",
    "’": r"'", "∞": r"$\infty$", "√": r"$\surd$", "∑": r"$\Sigma$", "∫": r"$\int$", "Å": r"\AA{}", "≃": r"$\simeq$",
    "∼": r"$\sim$", "…": r"...", "ϵ": r"$\epsilon$", "ℓ": r"$\ell$", "∂": r"$\partial$", "∇": r"$\nabla$",
    "★": r"*", "✓": r"ok", "⊥": r"$\perp$", "∥": r"$\parallel$",
}


def _codigo_latex(P):
    """copia src/*.py a informe/codigo/ sustituyendo los caracteres no ASCII por LaTeX (listings no admite UTF-8)"""
    d = P.informe / "codigo"
    d.mkdir(exist_ok=True)
    for f in sorted(P.src.glob("*.py")):
        out = []
        for ch in f.read_text():
            if ord(ch) < 128:
                out.append(ch)
            else:
                out.append("(*@" + UNICODE_LATEX.get(ch, "?") + "@*)")
        (d / f.name).write_text("".join(out))


def compilar_tex(archivo):
    archivo = Path(archivo)
    r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", archivo.name],
                       cwd=archivo.parent, capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        log = (archivo.parent / (archivo.stem + ".log"))
        txt = log.read_text(errors="replace") if log.exists() else r.stdout
        errores = [l for l in txt.splitlines() if l.startswith("!") or "Error" in l]
        i = txt.find("\n!")
        raise RuntimeError(f"Fallo LaTeX en {archivo}:\n" + "\n".join(errores[:10]) + "\n" + txt[i:i + 1500])
    subprocess.run(["latexmk", "-c", archivo.name], cwd=archivo.parent, capture_output=True)
    for ext in (".bbl", ".run.xml", ".nav", ".snm", ".vrb"):
        f = archivo.with_suffix(ext)
        if f.exists():
            f.unlink()
    print("  PDF", archivo.with_suffix(".pdf").name)


# ----------------------------------------------------------------------------------------- presentacion
def presentacion(P, meta, diapositivas, compilar=True):
    """diapositivas: lista de dict con 'titulo' y 'items' (lista de textos LaTeX) o 'figura' (+ 'nota')."""
    tex = [r"""\documentclass[aspectratio=169,10pt]{beamer}
\usetheme{Madrid}\usecolortheme{beaver}
\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[spanish,es-nodecimaldot,es-noquoting]{babel}\spanishplainpercent
\usepackage{amsmath,graphicx,booktabs}
\usepackage[output-decimal-marker={,},group-separator={\,},group-minimum-digits=4,exponent-product=\times,separate-uncertainty=true]{siunitx}
\setbeamertemplate{navigation symbols}{}
\DeclareUnicodeCharacter{2080}{\ensuremath{_0}}\DeclareUnicodeCharacter{2081}{\ensuremath{_1}}
\DeclareUnicodeCharacter{2082}{\ensuremath{_2}}\DeclareUnicodeCharacter{2083}{\ensuremath{_3}}
\DeclareUnicodeCharacter{2070}{\ensuremath{^0}}\DeclareUnicodeCharacter{00B9}{\ensuremath{^1}}
\DeclareUnicodeCharacter{2074}{\ensuremath{^4}}\DeclareUnicodeCharacter{2075}{\ensuremath{^5}}
\DeclareUnicodeCharacter{2076}{\ensuremath{^6}}\DeclareUnicodeCharacter{207B}{\ensuremath{^-}}
\DeclareUnicodeCharacter{03B1}{\ensuremath{\alpha}}\DeclareUnicodeCharacter{03B2}{\ensuremath{\beta}}
\DeclareUnicodeCharacter{03B3}{\ensuremath{\gamma}}\DeclareUnicodeCharacter{03B4}{\ensuremath{\delta}}
\DeclareUnicodeCharacter{03B5}{\ensuremath{\varepsilon}}\DeclareUnicodeCharacter{03B8}{\ensuremath{\theta}}
\DeclareUnicodeCharacter{03BB}{\ensuremath{\lambda}}\DeclareUnicodeCharacter{03BC}{\ensuremath{\mu}}
\DeclareUnicodeCharacter{03BD}{\ensuremath{\nu}}\DeclareUnicodeCharacter{03C0}{\ensuremath{\pi}}
\DeclareUnicodeCharacter{03C1}{\ensuremath{\rho}}\DeclareUnicodeCharacter{03C3}{\ensuremath{\sigma}}
\DeclareUnicodeCharacter{03C4}{\ensuremath{\tau}}\DeclareUnicodeCharacter{03C6}{\ensuremath{\phi}}
\DeclareUnicodeCharacter{03C7}{\ensuremath{\chi}}\DeclareUnicodeCharacter{03C9}{\ensuremath{\omega}}
\DeclareUnicodeCharacter{0394}{\ensuremath{\Delta}}\DeclareUnicodeCharacter{03A3}{\ensuremath{\Sigma}}
\DeclareUnicodeCharacter{2212}{\ensuremath{-}}\DeclareUnicodeCharacter{2248}{\ensuremath{\approx}}
\DeclareUnicodeCharacter{2264}{\ensuremath{\le}}\DeclareUnicodeCharacter{2265}{\ensuremath{\ge}}
\DeclareUnicodeCharacter{2192}{\ensuremath{\to}}\DeclareUnicodeCharacter{27E8}{\ensuremath{\langle}}
\DeclareUnicodeCharacter{27E9}{\ensuremath{\rangle}}\DeclareUnicodeCharacter{2032}{\ensuremath{'}}
\DeclareUnicodeCharacter{2033}{\ensuremath{''}}
""",
           rf"\title[Proyecto {meta['numero']}]{{Proyecto {meta['numero']}. {meta['titulo']}}}",
           rf"\subtitle{{{meta['area']}}}", rf"\author{{{AUTOR}}}", rf"\institute{{{CURSO}}}", r"\date{\today}",
           r"\begin{document}", r"\frame{\titlepage}"]
    for d in diapositivas:
        tex.append(rf"\begin{{frame}}{{{d['titulo']}}}")
        if "figura" in d:
            tex.append(r"\centering")
            tex.append(rf"\includegraphics[width=\linewidth,height=0.74\textheight,keepaspectratio]{{../figuras/{d['figura']}.pdf}}")
            if d.get("nota"):
                tex.append(rf"\\[2pt]{{\small {d['nota']}}}")
        else:
            tex.append(r"\begin{itemize}")
            tex += [rf"\item {i}" for i in d["items"]]
            tex.append(r"\end{itemize}")
        tex.append(r"\end{frame}")
    tex.append(r"\end{document}")
    salida = P.informe / "presentacion.tex"
    salida.write_text("\n".join(tex))
    if compilar:
        compilar_tex(salida)


# ----------------------------------------------------------------------------------------- README
def escribir_readme(P, meta, descripcion, resultados_md):
    """README.md del proyecto: objetivo, ejecucion, estructura y resultados principales"""
    archivos = "\n".join(f"| `{a}` | {t} |" for a, t in _arbol(P))
    txt = f"""# Proyecto {meta['numero']}. {meta['titulo']}

**Área:** {meta['area']} — **Nivel:** {meta['nivel']}

{descripcion}

## Ejecución

```bash
python3 src/simulacion.py   # datos simulados (datos/) y análisis (resultados/)
python3 src/graficas.py     # figuras (figuras/*.png, *.pdf)
python3 src/informe.py      # informe/informe.pdf, informe/presentacion.pdf y este README
```

Requiere Python 3 con NumPy, SciPy, Pandas y Matplotlib, y LaTeX (latexmk) para los PDF.
Los módulos comunes están en `../../comun/`. Las semillas están en `datos/parametros.json`.

## Resultados principales

{resultados_md}

## Archivos

| Archivo | Tamaño |
|---|---|
{archivos}
| `informe/informe.pdf` | informe científico |
| `informe/presentacion.pdf` | presentación final |
"""
    (P.raiz / "README.md").write_text(txt)
    print("  README.md")
