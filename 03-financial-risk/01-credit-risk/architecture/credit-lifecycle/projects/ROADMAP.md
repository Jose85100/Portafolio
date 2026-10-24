# Secuencia de desarrollo y puertas de evidencia

La prioridad indica qué incertidumbre conviene resolver primero, no una fecha prometida ni madurez implementada. La planificación está condicionada a contratos/datos y a la capacidad del equipo. Ningún proyecto nuevo pasó a S2 en esta entrega.

## A. Acordar la base común

Definir estados de evidencia y usos con [09](09-purpose-bound-signal-governance/README.md), contrato de versión/condiciones con [10](10-formalization-collateral/README.md) y fronteras de identidad de la [capa 01](../defense-layers/01-evidence-integrity/README.md). Resultado: diez contratos de ejemplo revisados como diseño y catálogo de invariantes; la revisión jurídica/operativa corresponde a responsables competentes.

## B. Tres primeros laboratorios acotados

| Primer prototipo propuesto | Qué reutiliza | Aporte concreto | Evidencia exigida |
|---|---|---|---|
| GEO-01 · radios/incertidumbre | Catálogo y vista de señales existentes | Medir cuándo la precisión reduce falsa discrepancia | Generador de trayectorias, baseline, errores por método y contraejemplos |
| PROV-02 · caída compartida | Notebook de dependencia/colas ya ejecutado | Añadir límite realista de reintento y costo de demora | Replay pareado, pendientes manuales/externos y costo factible |
| PAY-01 · respuesta incierta | Contratos y diseño de pagos | Comparar consulta de estado y reintento frente a operación liquidada | Emulador, invariante de efecto único y oráculo por intención |

No se crea otra versión de los notebooks existentes para aparentar independencia. La extensión mantiene referencia y evidencia propia. Las capas 01, 03, 05 y 08 acompañan esos laboratorios como controles y escenarios, no como servicios nuevos obligatorios.

## C. Integración de estados y calidad

Workflow [04](04-durable-origination-workflow/README.md) integra eventos/expiración con formalización y pago; ledger [06](06-servicing-ledger-quality/README.md) verifica saldos/DPD antes de decisiones de cartera. Después, ofertas [03](03-credit-offer-policy/README.md) y observabilidad [08](08-risk-data-observability/README.md) consumen esas interfaces según sus contratos, con datasets sintéticos separados de test.

## D. Tratamientos y retorno de incidentes

Cobranza [07](07-collections-treatment-design/README.md) parte de saldo/estado conciliados y acciones admisibles. Las capas de inteligencia, coordinación y vigilancia añaden hipótesis sobre dependencia y cambio, sin convertir alertas en labels. Los incidentes se adjudican antes de aprendizaje.

## Puerta mínima por etapa

| Puerta | Evidencia requerida | Motivo para detener promoción |
|---|---|---|
| Formulación S1 | Pregunta/unidad, supuestos, comparador, contrato y amenaza | Etiqueta ambigua o control que afirma un hecho no verificado |
| Prototipo S2 | Código, datos/semillas, baseline, oráculo/invariantes pertinentes, outputs y entorno | Experimento no ejecutado, fuga, falta de conservación o acción inválida |
| Validación S3 | Fuera de muestra, incertidumbre, costos y pruebas adversariales/legítimas | Ganancia que depende del test, extrapolación o daño sin evaluación |
| Uso institucional | Revisión independiente, habilitación, seguridad, operación y gobierno | Falta de autoridad, cobertura o condiciones de uso |

La última fila es una decisión institucional aparte; madurez científica no equivale a permiso de uso. No fijar un porcentaje universal de éxito sin prevalencia, horizonte, tamaño muestral y daño tolerable definidos.

## Propiedad e integración

Un propietario por proyecto; el índice, registro de ideas y capas son coordinación compartida. Las dependencias del registro describen contratos a acordar. Las implementaciones de los cuatro especialistas de fraude, MILP y módulos de IA siguen en sus carpetas originales. Una revisión independiente futura debe ser atribuida a quien efectivamente la realizó; aquí solo hay autorrevisión de consistencia documental.
