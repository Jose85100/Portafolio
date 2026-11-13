# Proyectos insignia

Cuatro proyectos sobre el crédito en Colombia, construidos con datos oficiales y pensados para las decisiones que se toman en
un comité de riesgo, en una función de validación, en una junta directiva y en un programa de investigación. Comparten una
sola [capa de datos](datos) y se conectan entre sí: el modelo de estrés del 01 es el objeto de la validación del 02, el
riesgo por producto del 01 alimenta el caso de inversión del 03, y el techo de usura que limita el precio en el 03 es la
regla de política que evalúa el 04.

| Proyecto | Pregunta | Resultado principal |
|---|---|---|
| [01 · Estrés macro y apetito de riesgo en consumo](01-riesgo-estres-consumo) | ¿Qué explicó el deterioro de 2023–2024, qué lo anticipaba y cuánto costaría un nuevo ciclo? | El deterioro fue de calidad de originación dentro de libre inversión y tarjeta (81% del cambio), no de mezcla. La mora de 31–60 días anticipa la mora 90+ de cada entidad con un trimestre de ventaja (t = 6,9). La expansión reciente del crédito ya trae incorporado un aumento de la mora en el escenario base. |
| [02 · Validación independiente del modelo satélite](02-validacion-modelo-satelite) | ¿Puede usarse ese modelo para estrés y límites? | No: 8 hallazgos, 4 de severidad alta. Estimado antes del ciclo, proyecta un pico de 9,0% frente a 4,8% observado y no supera al paseo aleatorio. El retador remediado (niveles con errores AR(1)) baja el error fuera de tiempo de 224 a 60 pb y le gana al paseo aleatorio a 12 meses (Diebold-Mariano p = 0,002). |
| [03 · Caso de inversión en crédito digital](03-caso-negocio-credito-digital) | ¿Conviene entrar, con qué producto, qué fondeo y qué escala? | Con la TPM en 12,25% y el techo de usura en 28,3%, el fondeo mayorista no deja negocio (ROE máximo 1%). La configuración viable es banco digital con depósitos, tarjeta para adquirir y libre inversión cruzada a clientes con historial, desde 800.000 clientes de tarjeta (TIR 23,7% frente a 11,6% de la tarjeta sola). |
| [04 · ¿Raciona crédito el techo de usura?](04-usura-racionamiento-credito) | Evidencia causal sobre una regla de política | Hay amontonamiento fuerte justo debajo del techo. Un recorte obliga a las celdas pegadas al techo a bajar 0,34 pp su tasa y reduce 2,8% el número de créditos sin cambiar el ticket: racionamiento en el margen extensivo. La primera versión del diseño se descartó por tendencias previas y queda documentada. |

## Cómo se trabajó

- **Datos oficiales y trazables.** SFC (cartera por calificación y mora, tasas y desembolsos semanales, interés bancario
  corriente), Banco de la República (tasa de política) y DANE (GEIH, IPC, ISE). La [capa de datos](datos) descarga, normaliza,
  reconcilia y registra SHA-256 de cada insumo.
- **Iteraciones visibles.** Cada notebook conserva las hipótesis que fallaron y por qué: el desempleo no anticipa la mora en
  esta muestra; la selección por AIC daba un signo de tasa contrario a la teoría; la primera definición de tratamiento del
  estudio de eventos seleccionaba alzas transitorias; el primer caso de negocio no era rentable con fondeo mayorista.
- **Supuestos separados de los datos.** Las LGD, los costos y el CAC están declarados en un solo lugar y sometidos a
  sensibilidad y Monte Carlo.
- **Pruebas.** `tests/test_insignia.py` verifica las identidades y los invariantes de cada módulo; los notebooks incluyen
  `assert` sobre los resultados centrales.

## Reproducir

```bash
pip install -r ../requirements-research.txt
python3 datos/construir_datos.py --descargar   # baja los crudos (~350 MB, no versionados)
python3 datos/construir_datos.py               # reconstruye datos/procesados
for p in 01-riesgo-estres-consumo 02-validacion-modelo-satelite 03-caso-negocio-credito-digital 04-usura-racionamiento-credito; do
  (cd $p && python3 construir_notebook.py)
done
python3 -m unittest discover -s tests -v
```

Los datos procesados ya están versionados, así que los notebooks corren sin descargar nada.
