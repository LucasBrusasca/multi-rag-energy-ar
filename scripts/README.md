# Scripts operativos

Este directorio contiene puntos de entrada auxiliares, no módulos del sistema.

- `admin/`: acciones explícitas de administración. Algunas consultan o modifican
  PostgreSQL; deben ejecutarse conscientemente.
- `diagnostics/`: comprobaciones manuales para desarrollo. No son tests ni
  evidencia experimental.

Ejecutar siempre desde la raíz y como módulo, por ejemplo:

```powershell
python -B -m scripts.admin.ver_base
python -B -m scripts.diagnostics.check_router "consulta"
python -B -m scripts.diagnostics.infoleg_html_pilot
python -B -m scripts.diagnostics.infoleg_structure_ablation
python -B -m scripts.diagnostics.sonda_indices_alcance --planes
```

Las pruebas automatizadas viven exclusivamente en `tests/`. Los experimentos
de tesis y sus resultados viven exclusivamente en `experimentos/`.
