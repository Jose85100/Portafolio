# Broker read-only con autoridad anclada a descriptor

MVP defensivo del pilar 08: una propuesta de tool call no concede permisos. Un grant confiable fija el directorio raíz y un límite de bytes; el broker valida un esquema exacto y abre componentes relativos con descriptores de directorio y `O_NOFOLLOW`. Sólo lee archivos regulares UTF-8 y no ejecuta comandos, writes ni red.

## Reproducir

Linux/Python 3.12 con pip, desde esta carpeta:

```bash
bash run.sh
```

Instala herramientas de notebook fijadas; ejecuta 10 tests, 288 solicitudes de prueba y notebook. Núcleo de biblioteca estándar. Entorno preparado: `PYTHON=/ruta/python SKIP_INSTALL=1 bash run.sh`.

Todas las fixtures están en directorios temporales creados por el experimento. El canario exterior también es sintético y está dentro de ese mismo TemporaryDirectory. No se accede a secretos, archivos de usuario ni servicios reales; no se llama a un LLM.

## Evidencia ejecutada

Ocho repeticiones × 12 casos × tres políticas. Siete casos intentan leer el canario exterior, tres miden utilidad benigna y dos validan esquema/presupuesto.

| Política | Lecturas de canario / 56 casos de escape | Lecturas benignas / 24 |
|---|---:|---:|
| Prefijo textual | 56 | 24 |
| Resolver y después abrir | 24 | 24 |
| Descriptor anclado | 0 | 16 |

`resolve_then_open` bloquea ataques estáticos de ruta, pero los dos interleavings TOCTOU inyectados y un hardlink estático lo eluden. `anchored_fd` elimina esas lecturas en esta suite, **a costa de rechazar también ocho aliases symlink internos legítimos**. Cero escapes aquí no certifica seguridad general ni resistencia a prompt injection en lenguaje natural.

## Contrato y límites

Request exacta: `{"tool":"read_text","path":"report.txt","max_bytes":4096}`. No campos extra ni bool como entero. El root y cap son configuración confiable; el request no puede ampliarlos. Hardened requiere ruta relativa sin componentes vacíos, punto o parent; máximo 16 componentes/256 caracteres. Rechaza todos los symlinks, archivos no regulares y hardlinks detectados por nlink. max_bytes limita la respuesta aceptada; se inspecciona como máximo un byte adicional para detectar y rechazar archivos demasiado grandes.

El grant autoriza objetos alcanzados desde el descriptor: al renombrar un padre ya abierto, el descriptor conserva el objeto original. No garantiza que su pathname actual siga siendo descendiente del root. No cubre mounts hostiles, kernel, adversario que crea/elimina hardlinks entre controles, cambios maliciosos de contenido, raíz de grant no confiable, permisos multi-tenant ni sandbox de procesos. El ciclo de vida del broker tiene propietario único; no cubre carreras entre close/read del propio broker. No es sustituto de contenedores/openat2/políticas de SO revisadas.

`fault_hook` es instrumentación Python confiable fuera del payload: fuerza un interleaving después del check/adquisición del descriptor padre. No es un hook accesible a la solicitud ni una carrera probabilística real.

## Entregables y madurez

`src/`, `tests/`, `results/raw.csv`, `summary.json`, SVG, notebook ejecutado, configuración, cinco referencias primarias y `informe.md` con 14 puntos/selección de tres ideas. No se guardan contenidos leídos ni paths temporales absolutos en CSV. Componente S2 del programa antes S1; candidato M2 local sujeto a revisión técnica, no operacional. Notebook IPython in-process, no kernel aislado.
