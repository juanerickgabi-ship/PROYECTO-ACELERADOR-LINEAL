"""Estilo comun de las figuras: tamano de pagina, fuentes legibles y guardado en PNG y PDF."""
import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt

ANCHO = 7.5      # pulgadas: la figura se reduce poco al ancho de la pagina, los textos quedan a 9-10 pt
COLORES = ["#1f5fa8", "#d1495b", "#2e9e6a", "#7b4fb3", "#e08a1e", "#3fa7c4", "#8a5a44", "#555555"]


def aplicar(**extra):
    mpl.rcParams.update({
        "font.size": 11, "axes.labelsize": 12, "axes.titlesize": 12, "xtick.labelsize": 10.5,
        "ytick.labelsize": 10.5, "legend.fontsize": 9.5, "legend.frameon": False, "axes.grid": True,
        "grid.color": "#e2e2e2", "grid.linewidth": 0.7, "axes.spines.top": False, "axes.spines.right": False,
        "axes.prop_cycle": mpl.cycler(color=COLORES), "lines.linewidth": 1.8,
        "savefig.dpi": 200, "savefig.bbox": "tight", "figure.dpi": 100, "mathtext.fontset": "dejavuserif"})
    mpl.rcParams.update(extra)


def figura(nfil=1, ncol=1, alto=None, ancho=ANCHO, **kw):
    """crea una figura con el estilo comun; alto por defecto proporcional al numero de filas"""
    aplicar()
    alto = alto or (3.6 * nfil + 0.4)
    return plt.subplots(nfil, ncol, figsize=(ancho, alto), **kw)


def guardar(fig, P, nombre):
    """guarda figuras/<nombre>.png y .pdf del proyecto P"""
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(P.figuras / f"{nombre}.{ext}")
    plt.close(fig)
    print("  figura", nombre)


def letra(ax, txt, x=0.02, y=0.96):
    """etiqueta de panel (a), (b), ..."""
    ax.text(x, y, txt, transform=ax.transAxes, fontsize=12, fontweight="bold", va="top")
