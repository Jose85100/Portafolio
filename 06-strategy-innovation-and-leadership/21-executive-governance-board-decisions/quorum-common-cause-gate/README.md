# Quorum Common-Cause Gate

Auditar la disponibilidad de un **comité operativo hipotético** cuando varias ausencias comparten una causa. El evento es poder formar un mínimo fijo de3personas con el responsable de riesgo presente; no mide votos favorables, calidad de decisiones ni validez jurídica de una junta.

Componente S2 sintético en programa21, que conserva S1 fuera de este componente. No prescribe composición real, nombramientos o cambios de estatutos.

## Reproducir

Python3.12, desde esta carpeta:

```bash
bash run.sh
```

Instala versiones directas fijadas, corre tests/cobertura, ruff, mypy, benchmark y notebook. Con entorno existente: `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`. Ejecución local en venv con paquetes científicos disponibles; segundo contenedor limpio no probado. Transitivas sinhash. SinAPI ni datos personales.

## Decisión sintética

| Reservas autorizadas | Probabilidad exacta | Independencia marginal | Costo |
|---:|---:|---:|---:|
|0|0,7600|0,8512|0|
|1|0,7600|0,93328|1|
|2|0,9139|0,947644|2|

Meta0,85: el baseline independiente recomienda0reservas y da un falso pase; el diseño exacto necesita2. Se gana15,39puntos de disponibilidad a costo2unidades. No se demuestra rentabilidad ni efectividad real de gobierno.

La causa común afecta a3miembros simultáneamente. Las reservas tienen disponibilidad0,9 independiente entre sí ydelrégimen **por supuesto**. El responsable de riesgo no se sustituye. Todos los adicionales se suponen elegibles/autorizados y cuentan hacia el mínimo fijo3; al crecer N, cambia la fracción representada por ese mínimo. No sirve directamente para una regla jurídica de mayoría o quórum proporcional al tamaño.

## Límites y artefactos

`config.json`:2regímenes,4miembros base, menú0/1/2reservas. `src/quorum.py`: enumeración2^N y ley de probabilidad total, validada hasta16miembros. `results/`: planes,224masas de estados crudas (incluidos ceros), sensibilidad, escalabilidad, JSON yPNG. Notebook ejecutado,5referencias DOI/URL e informe14puntos.

Con disrupción0,8, el menú no alcanza meta. Rol obligatorio0,95 impone cota≤0,95: meta0,97inviable. Si el mínimo se eleva a4, tampoco se arregla con este menú. No se reduce el requisito para forzar éxito. Ausencias reales, independencia de reservas, conflictos, agendas ycalidad no están calibrados.

Notebook realmente ejecutado en IPython en proceso con namespace fresco ycaptura rich; noQA kernelJupyter. PNG inspeccionado; interfaz notebook completa no inspeccionada.

## Continuidad30oct: las reservas también fallan

Se profundiza esta misma herramienta, sin crear otra demo. `src/reserve_ambiguity.py` mantiene el evento29 y reemplaza independencia de2reservas durante disrupción por cotas sharp clásicas. Para marginalesq1/q2:

\[
\max(0,q_1+q_2-1)\le p_{11}\le\min(q_1,q_2),\quad
P(E)=r[(1-s)+sp_{11}].
\]

El notebook existente conserva elcaso29 y añade una derivación desde la tabla2×2, oracles, ablations separadas, fronteras de decisión y preguntas para el lector. `bash run.sh` reproduce ambas iteraciones.

| Opción hipotética para el mismo par autorizado | q1=q2 en shock | Costo | Pnominal | Cota inferior |
|---|---:|---:|---:|---:|
|A|0,7|2|0,8531|0,836|
|B|0,8|3|0,8816|0,874|
|C|0,9|4|0,9139|0,912|

Nominal eligeA ypuede incumplir0,85; robustoeligeB pagando1unidad adicional. La garantía cubre solo elpar ylasmarginales dadas: elrolobligatorio sigue independiente condicionalmente. Dependencia positiva perfecta conq0,7da0,893, superior alnominal; elpeorcaso amplio incluye dependencia negativa. No se afirma que toda correlación dañe disponibilidad.

Resultados30en `results/dependence_*`, `reserve_couplings.csv`, `config_dependence.json`. Suite acumulada10tests,100%133statements núcleo, LPindependiente yrecuperación delmotor29. Véanse `matriz_prior_art.md`, `RESEARCH_LOG.md`, `ROADMAP.md` e `informe-2026-10-30.md`.6referencias verificadas con cobertura explícita. ComponenteS2 sintético; no certificar un programa operativo.


## Continuidad31: el rol obligatorio también puede depender

Misma carpeta, evento y comando `bash run.sh`. Nuevo `src/joint_role.py`: cotas puntuales para la intersección de tres eventos. `benchmarks/joint_role_run.py` contrasta un LP de ocho variables y guarda testigos. `derivacion-2026-10-31.md` y el notebook acumulativo explican la transformación30→31. Configuración: `config_joint_role.json`; resultados: `results/joint_role_*`; informe de14 puntos: `informe-2026-10-31.md`.

PlanB: cota anterior0,874 → nueva cota0,870. La meta original0,85 sigue eligiendoB. La frontera diseñada0,872 cambia deB(costo3) aC(costo4). Sin datos reales ni garantía fuera de marginales, regímenes y evento documentados. Costos abstractos; no se certifica cumplimiento legal o calidad decisional. Adaptación y auditoría de una cota clásica; componenteS2 sintético, no programa validado u operacional. Quince tests acumulados y cobertura medida100% de155 statements del núcleo; revisión independiente local realizada.


## Continuidad del1 de noviembre: caja supuesta de parámetros

Mismo comando `bash run.sh` y carpeta. `src/interval_role.py` añade intervalos de probabilidades y selección por certificado de caja; reutiliza el motor31. `config_intervals.json` declara escenarios, semilla nula, fuentes/entorno y ausencia de cobertura estadística. Derivación en `derivacion-2026-11-01.md` y notebook acumulativo; resultados CSV/JSON/PNG `results/interval_*`; informe14 puntos en `informe-2026-11-01.md`.

B tenía cota puntual0,870; con r±0,01, q1/q2±0,02 y shock±0,01, la cota cae a0,8476. Al mismo umbral0,85, C cuesta una unidad más y certifica0,8896 dentro de la caja asumida. No hay intervalos de confianza estimados ni observaciones: no significa95% de seguridad estadística. Se conservan recuperación puntual, inviabilidad y costos de robustez. Adaptación de ingeniería, componenteS2 sintético; no operación o validación empresarial. Reproducción, revisión y CI se registran por separado en el informe.


## Continuidad del2 de noviembre: información conjunta requerida

Mismo comando `bash run.sh`. `src/pair_assurance.py` añade certificado con un piso supuesto de coasistencia del par y calcula el mínimo requerido para conservar una opción. Reutiliza intervalos y caja01nov. Configuración `config_pair_assurance.json`, derivación LaTeX `derivacion-2026-11-02.md`, notebook acumulativo y resultados `results/pair_*`; informe14 puntos en `informe-2026-11-02.md`.

B tiene cota de caja0,8476. Si una restricción válida garantizara coasistencia del par durante shock≥0,65, su certificado sería0,8665 y permitiría conservar costo3 frente a4 deC. El mínimo requerido para la meta0,85 es4/7≈0,57143. Esto es una **pregunta para evidencia futura**, no evidencia obtenida, ahorro realizado o confianza95%. Piso redundante no aporta; incompatible se rechaza. C sigue siendo la opción certificada sin esa restricción adicional. Adaptación de ingeniería, componenteS2 sintético; no programa validado u operacional.
