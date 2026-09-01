# Piloto aislado de Marker

Marker es un parser challenger para PDFs, no una dependencia del pipeline. Se
instala en otro entorno porque `marker-pdf==2.0.0` requiere Pillow `<11` y
Transformers `>=5.12.1`, mientras el proyecto usa Pillow 12.2.0 y Transformers
5.9.0.

```powershell
.\.venv\Scripts\python.exe -m venv .venv-marker
.\.venv-marker\Scripts\python.exe -m pip install `
  -r scripts\diagnostics\marker\requirements-marker.txt
```

En CPU, Surya 0.22.1 requiere además el ejecutable `llama-server`; Marker no lo
declara como dependencia Python. Para este piloto se congeló el release oficial
`llama.cpp b10612`, asset `llama-b10612-bin-win-cpu-x64.zip`, SHA-256
`4481a3550d4b70132fb7e1f1973cc8c19e761a9c64d3f37fa78241dd3fcdf5b5`.
El archivo `llama.cpp-release.json` conserva esos datos para reproducibilidad.

Primera corrida reproducible, sin LLM y sin modificar la ingesta:

```powershell
.\.venv\Scripts\python.exe -B scripts\diagnostics\benchmark_marker_tablas.py `
  --run-marker `
  --marker-python .\.venv-marker\Scripts\python.exe `
  --llama-cpp-binary .\.venv-marker\tools\llama.cpp\b10612\llama-server.exe `
  --modo-marker fast `
  --documentos-marker Transener_Calificacion_FIX.pdf `
  --repeticiones 1
```

Para medir estabilidad se usan dos repeticiones. `balanced` se prueba después
en una máquina con GPU y siempre como brazo separado. El modo con LLM no forma
parte del primer piloto: añade proveedor, costo y una posible fusión de tablas
entre páginas que debe auditarse también por procedencia.

Si `run_01` ya existe, una segunda corrida se agrega sin pisarla mediante
`--repeticion-inicial 2 --repeticiones 1`. El runner registra duración, SHA-256
y pico de RSS del árbol de procesos en `marker/run_metadata.json`.

Los resultados quedan bajo `experimentos/auditoria_tablas/marker/` y
`experimentos/auditoria_tablas/comparacion_parsers/`. Los casos del manifest
son semillas exploratorias: deben verificarse visualmente y congelarse antes
de convertirse en Golden confirmatorio.

La decisión y los resultados observados del piloto están registrados en
`experimentos/auditoria_tablas/marker/RESULTADO_PILOTO.md`.

Hallazgo del piloto: el renderer `chunks` de Marker 2.0.0 escribió, por ejemplo,
`page=374` en un bloque con ID `/page/0/Table/11`. El adaptador no confía en ese
campo: reconstruye la página desde el segmento estable `/page/N/` del ID y deja
declarada esa política en cada informe. Esto repara la comparación, pero el bug
de procedencia sigue contando contra una adopción directa del formato.

Los `.xlsx` no se procesan con Marker. Se leen mediante `openpyxl` y se auditan
con `scripts/diagnostics/auditar_excel.py`, porque pasar celdas a PDF destruye
la grilla, los encabezados combinados y la semántica de las hojas.
