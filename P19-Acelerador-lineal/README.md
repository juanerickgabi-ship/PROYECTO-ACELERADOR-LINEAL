# Proyecto 19. Acelerador lineal

**Área:** Aceleradores — **Nivel:** III cx

Linac de protones de tubos de deriva: diseño de celdas βλ, dinámica longitudinal de un paquete, estabilidad de fase, oscilaciones de sincrotrón, error de frecuencia y electrones.

## Ejecución

```bash
python3 src/simulacion.py   # datos simulados (datos/) y análisis (resultados/)
python3 src/graficas.py     # figuras (figuras/*.png, *.pdf)
python3 src/informe.py      # informe/informe.pdf, informe/presentacion.pdf y este README
```

Requiere Python 3 con NumPy, SciPy, Pandas y Matplotlib, y LaTeX (latexmk) para los PDF.
Los módulos comunes están en `../../comun/`. Las semillas están en `datos/parametros.json`.

## Resultados principales

- 3 → 50 MeV, qV = 1 MeV, φs = −30°: 55 celdas, 10.59 m (celdas de 7.7 a 26.9 cm).
- Paquete agrupado: 100.0 % (−60°), 99.3 % (−30°); en la cresta solo 24.1 % llega a la energía final.
- Avance de fase de sincrotrón: 25.7°/celda simulado frente a 26.4° teórico.
- Electrones (β≈1): sin oscilaciones; energía final ∝ cos φ de inyección.

## Archivos

| Archivo | Tamaño |
|---|---|
| `datos/fase_media_error0.0.npy` | 0.4 kB |
| `datos/fase_media_error0.002.npy` | 0.4 kB |
| `datos/fase_media_error0.005.npy` | 0.4 kB |
| `datos/fase_media_error0.01.npy` | 0.4 kB |
| `datos/fase_media_error0.02.npy` | 0.4 kB |
| `datos/fase_media_error0.04.npy` | 0.4 kB |
| `datos/paquete_fase-15.npz` | 300.1 kB |
| `datos/paquete_fase-30.npz` | 334.7 kB |
| `datos/paquete_fase-60.npz` | 568.0 kB |
| `datos/paquete_fase0.npz` | 286.5 kB |
| `datos/paquete_fase30.npz` | 326.4 kB |
| `datos/parametros.json` | 0.4 kB |
| `src/graficas.py` | 3.4 kB |
| `src/informe.py` | 16.8 kB |
| `src/modelo.py` | 2.6 kB |
| `src/simulacion.py` | 5.4 kB |
| `resultados/avance_sincrotron.csv` | 0.1 kB |
| `resultados/celdas_vs_fase.csv` | 0.1 kB |
| `resultados/diseno_celdas.csv` | 1.6 kB |
| `resultados/electrones.csv` | 5.1 kB |
| `resultados/error_frecuencia.csv` | 0.2 kB |
| `resultados/estabilidad_fase.csv` | 0.5 kB |
| `resultados/oscilacion_pequena.csv` | 1.2 kB |
| `resultados/resumen.json` | 0.6 kB |
| `figuras/fig01_diseno.pdf` | 19.4 kB |
| `figuras/fig01_diseno.png` | 82.2 kB |
| `figuras/fig02_espacio_fases.pdf` | 76.1 kB |
| `figuras/fig02_espacio_fases.png` | 87.8 kB |
| `figuras/fig03_sincrotron.pdf` | 21.2 kB |
| `figuras/fig03_sincrotron.png` | 110.7 kB |
| `figuras/fig04_estabilidad_electrones.pdf` | 27.0 kB |
| `figuras/fig04_estabilidad_electrones.png` | 174.2 kB |
| `informe/informe.pdf` | informe científico |
| `informe/presentacion.pdf` | presentación final |
