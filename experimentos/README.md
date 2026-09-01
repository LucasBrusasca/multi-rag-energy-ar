# Experimentos de la tesis

Este directorio conserva instrumentos, corridas y resultados experimentales.
No contiene código de producción.

## Clasificación

- `2026-07-25_silos/`: exploración histórica inicial de silos.
- `2026-07-26_estado/`: auditoría exploratoria histórica; sus números siguen en
  suspenso según su propio README.
- `golden_piloto_v0.yaml`: instrumento piloto versionado.
- `golden_piloto_borrador.md`: material de preparación, no Golden congelado.
- `casos_regresion_desarrollo.md`: casos para desarrollo, no test confirmatorio.
- `sonda_respuestas.json`: salida de una sonda, no conclusión de tesis.
- `LECCIONES_METODOLOGICAS.md`: reservas y aprendizajes metodológicos.

Los directorios fechados se preservan en su ubicación original porque sus
scripts calculan rutas relativas desde ella. No deben importarse desde el código
activo ni usarse como biblioteca. Una nueva corrida confirmatoria debe crear su
propio directorio fechado, manifest y artefactos, sin sobrescribir los anteriores.
