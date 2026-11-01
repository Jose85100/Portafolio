# MVP

- Qué: prueba de disponibilidad de comité con mínimo fijo y rol obligatorio bajo ausencias de causa común.
- Corre: `bash run.sh`; entorno preparado `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`.
- Produce: plan mínimo del menú, falso pase de independencia marginal,224estados crudos, sensibilidad/scaling, figura y notebook ejecutado.
- No cubre: votos, calidad, nombramientos, validez jurídica, quórum proporcional, conflictos o probabilidades empíricas.
- Decisión: considerar2reservas solo si elegibilidad/independencia están justificadas; ajustar supuestos/calendario si hay causa común; rechazar si no existe plan factible sin alterar restricciones.
- Madurez: componenteS2 sintético, programa21S1; no equivalencia automáticaM2 ni operación.
- Negativos:1reserva no ayuda en el evento crítico; peso shock0,8/meta0,97/mínimo4 dan inviabilidad del menú.
- Checklist: src✓ comando✓ tests✓ baseline✓ CSV/JSON/PNG✓ notebookoutputs✓5refs✓ informe14p✓ README/MVP/entorno✓ carpeta21✓ madurezlocal✓. Revisión y publicación separadas, sinmerge automático.

## Extensión acumulativa30oct
- Mismo evento/componente/notebook; mantiene módulo ytests29.
- Nuevo: acoplamiento arbitrario delpar de reservas en shock, marginales distintas yselección por cota sharp inferior.
- Pipeline único `bash run.sh`;10tests,LPindependiente,133statements100%,6refs, matriz/log/roadmap.
- Enseña derivaciónLaTeX ysepara cambio de marginales delcambio de dependencia.
- No cubre dependencia delrol0, error de marginales oreglas jurídicas. Adaptación clásica, no teorema nuevo.


## Continuidad31: el rol obligatorio también puede depender

Misma carpeta, evento y comando `bash run.sh`. Nuevo `src/joint_role.py`: cotas puntuales para la intersección de tres eventos. `benchmarks/joint_role_run.py` contrasta un LP de ocho variables y guarda testigos. `derivacion-2026-10-31.md` y el notebook acumulativo explican la transformación30→31. Configuración: `config_joint_role.json`; resultados: `results/joint_role_*`; informe de14 puntos: `informe-2026-10-31.md`.

PlanB: cota anterior0,874 → nueva cota0,870. La meta original0,85 sigue eligiendoB. La frontera diseñada0,872 cambia deB(costo3) aC(costo4). Sin datos reales ni garantía fuera de marginales, regímenes y evento documentados. Costos abstractos; no se certifica cumplimiento legal o calidad decisional. Adaptación y auditoría de una cota clásica; componenteS2 sintético, no programa validado u operacional. Quince tests acumulados y cobertura medida100% de155 statements del núcleo; revisión independiente local realizada.


## Continuidad del1 de noviembre: caja supuesta de parámetros

Mismo comando `bash run.sh` y carpeta. `src/interval_role.py` añade intervalos de probabilidades y selección por certificado de caja; reutiliza el motor31. `config_intervals.json` declara escenarios, semilla nula, fuentes/entorno y ausencia de cobertura estadística. Derivación en `derivacion-2026-11-01.md` y notebook acumulativo; resultados CSV/JSON/PNG `results/interval_*`; informe14 puntos en `informe-2026-11-01.md`.

B tenía cota puntual0,870; con r±0,01, q1/q2±0,02 y shock±0,01, la cota cae a0,8476. Al mismo umbral0,85, C cuesta una unidad más y certifica0,8896 dentro de la caja asumida. No hay intervalos de confianza estimados ni observaciones: no significa95% de seguridad estadística. Se conservan recuperación puntual, inviabilidad y costos de robustez. Adaptación de ingeniería, componenteS2 sintético; no operación o validación empresarial. Reproducción, revisión y CI se registran por separado en el informe.
