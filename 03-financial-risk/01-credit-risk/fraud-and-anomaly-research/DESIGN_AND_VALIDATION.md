# Contratos, etiquetas y validación común

**Estado: especificación S1.** Este documento define los requisitos para implementar los cuatro proyectos; no incorpora una base real ni código de scoring.

## 1. Separar hechos, decisiones y resultados

La tabla de solicitudes representa lo conocido al pedir crédito. Las verificaciones contienen evidencia y su disponibilidad. Las decisiones documentan lo que hizo una política o un analista. Los resultados adjudicados indican qué se pudo confirmar después. Rechazar una solicitud no la convierte en fraude y aprobarla no demuestra legitimidad.

Catálogo de estados: `confirmed_fraud`, `confirmed_legitimate`, `suspected`, `inconclusive`, `pending`. Guardar además tipología, fecha del hecho, fecha del reporte, fecha de adjudicación, fuente de evidencia, revisor, versión y eventual reversión. La ausencia de denuncia no será automáticamente `confirmed_legitimate`.

Mantener cuatro etiquetas de tipología, que pueden coexistir: suplantación/identidad sintética; coordinación en red; tergiversación documental o de ingreso; manipulación del proceso. Conservar default y mora en tablas diferentes. Una pérdida no recuperada y un fraude confirmado son variables distintas.

## 2. Tablas propuestas

| Tabla | Grano y campos mínimos | Restricción principal |
|---|---|---|
| `applications` | `application_id`, `customer_token`, `submitted_at`, producto, canal, monto, moneda, versión | ID único; montos finitos y no negativos |
| `verification_events` | ID, solicitud, tipo, `event_at`, `available_at`, resultado, proveedor, versión, calidad | Una corrección agrega versión, no sobrescribe historia |
| `entity_links` | Solicitud, tipo de entidad, token, `event_at`, `available_at`, confianza del enlace | Sin números de documento, teléfonos o cuentas en claro |
| `income_observations` | Solicitud, período, ingreso declarado/observado, moneda, cobertura, fuente, disponibilidad | Distinguir cero, no observado y no aplicable |
| `process_events` | ID de evento, solicitud, etapa, actor tokenizado, canal, tiempos, versión de política | Deduplicar por ID; conservar eventos tardíos |
| `case_outcomes` | Caso, solicitudes vinculadas, estado, evidencia, tiempos, tipología, pérdida, recuperación | Historial de adjudicación y revisión |
| `model_outputs` | Solicitud/caso, corte, versión, score, tipo de score, razones, cobertura, acción sugerida | Un score de anomalía no se publica como probabilidad |

Las claves y los tipos anteriores son una especificación, no un DDL aplicado. La implementación institucional debe definir acceso, retención, minimización y tokenización resistente a ataques de diccionario; un hash simple de documento no es anonimización. El repositorio público no recibirá PII, biometría ni documentos originales.

## 3. Disponibilidad temporal y joins

Para decidir en `t`, una variable solo puede usar registros con `event_at <= t` **y** `available_at <= t`. Si un proveedor corrige el ingreso días después, la corrección no entra en una reconstrucción del corte anterior. Los agregados usan ventanas `[t-w,t)` y excluyen la solicitud evaluada; las señales de esa solicitud se incorporan por separado al completar su etapa.

En una consulta histórica de vecinos fraudulentos se exige que la adjudicación estuviera disponible antes de `t`. El entrenamiento a fecha `T` solo ve etiquetas adjudicadas hasta `T`; el test puede madurar después para evaluarlo, pero nunca alimenta el ajuste ni la construcción histórica de variables.

## 4. Protocolo experimental

1. Fijar corte de entrenamiento, validación y test por fecha de solicitud. Reservar un período de maduración y un embargo acorde con la ventana de resultados, no una duración universal.
2. Ajustar imputación, escalado, selección de variables, reglas aprendidas, pesos de clase y calibración únicamente en entrenamiento/validación según su función. El test queda cerrado.
3. Separar ventanas para selección de hiperparámetros y calibración o usar validación temporal anidada. Nunca calibrar sobre el test.
4. Reportar dos evaluaciones: temporal operativa, que permite clientes recurrentes usando solo su pasado, y generalización a clientes/componentes nuevos con separación de grupos. No afirmar que son la misma población.
5. Congelar versión de fuentes, generador, parámetros, semilla, dependencias y versión de código. Publicar tablas por cohorte, diagrama de exclusiones y razones de datos faltantes.
6. Comparar reglas, modelo y combinación con igual capacidad `K` por día. Examinar empates, días sin casos positivos y días con menos de `K` solicitudes. El desempate será determinista.

Etiquetas escasas: muestrear también solicitudes sin alerta para revisión, con probabilidades de selección conocidas. El ponderador inverso puede corregir estimaciones solo donde existe soporte; no resuelve poblaciones nunca observadas. Sin cobertura de verificación, reportar precisión en revisados y límites de identificación, no recall poblacional ficticio. Positivos-no etiquetados es un challenger bajo supuestos explícitos, no un reemplazo de adjudicación.

## 5. Métricas y decisiones económicas

Con `TP`, `FP`, `FN` definidos sobre una población adjudicada, `precision=TP/(TP+FP)` y `recall=TP/(TP+FN)`. Si el denominador es cero, registrar no definido. Reportar AP, precisión/recall a `K`, falsos positivos por 1.000 solicitudes legítimas verificadas, cobertura de etiquetas y latencia de detección. AP se calcula como `sum((R_n-R_(n-1))*P_n)`, indicando implementación y prevalencia. ROC-AUC será complementaria.

Para priorizar, una aproximación de beneficio de revisión es:

`V_i = p_i * L_i * q_i - c_review_i - (1-p_i)*c_friction_i`.

Aquí `p` exige calibración, `L` es pérdida neta esperada condicionada a fraude, `q` es fracción prevenible por investigar, y los costos comparten moneda y horizonte. Elegir hasta `K` casos con `V_i>0` es una heurística si tiempos son iguales; con tiempos distintos debe resolverse una asignación bajo capacidad. Una alerta sin investigar no equivale a pérdida evitada.

Ejemplo exclusivamente ilustrativo: con `p=0,08`, `L=2.000.000 COP`, `q=0,60`, costo de revisión `15.000` y fricción `10.000`, el valor aproximado es `71.800 COP`. No es un resultado observado ni prueba causal. Para medir pérdidas evitadas, una comparación histórica simple mezcla selección y política; diseñar un piloto controlado de revisión adicional sobre casos elegibles, conservando controles obligatorios.

Proponer intervalos por bootstrap en bloques temporales y, para redes, por componentes/casos. Informar pocas campañas o pocos positivos como limitación. Los segmentos de producto, canal, antigüedad y cobertura de datos requieren precisión, fricción y tasa de derivación separadas. No usar atributos protegidos como evidencia de fraude.

## 6. Pruebas de aceptación antes de S2

- Agregar eventos futuros no modifica salidas pasadas; mover `available_at` cambia únicamente cortes posteriores.
- Duplicar un evento no altera conteos; reordenar eventos da el mismo resultado; timestamps inválidos se rechazan.
- Un dispositivo compartido legítimo, un ingreso informal y un cambio autorizado de política forman controles negativos obligatorios.
- La supresión de una fuente produce cobertura degradada explícita, no score cero ni veredicto adverso por defecto.
- Scores probabilísticos permanecen finitos entre 0 y 1; scores de novedad declaran orientación y escala.
- Las métricas separan solicitud y caso; una red con diez solicitudes no crea diez fraudes independientes en el intervalo.
- Los resultados agregados reconcilian con las cohortes; no se suman fraude y pérdida crediticia sobre el mismo flujo sin conciliación.

## 7. Operación propuesta y límites

Emitir razones trazables a variables y evidencia verificable. La revisión tendrá estados de espera, investigación, resolución y apelación, con deduplicación y control de carga. El sistema propondrá verificación adicional, no una acusación automática. Mantener políticas y overrides versionados y limitar acceso a evidencia sensible.

En sombra medir volumen, tiempo por caso, demora de etiqueta, datos faltantes, deriva y conversión de clientes legítimos. Un fallo de proveedor debe abrir un incidente de calidad y activar una ruta de verificación alternativa definida; no disparar una actualización automática del modelo. La promoción exige revisión independiente, evaluación institucional de privacidad y un plan de reversión. No se afirma conformidad regulatoria con esta especificación.
