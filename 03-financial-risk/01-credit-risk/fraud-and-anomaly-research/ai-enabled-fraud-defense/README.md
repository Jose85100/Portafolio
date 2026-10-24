# Fraude potenciado por IA: defensa por capas

Corte: **23 de octubre de 2026**. Extensión de las cuatro líneas de fraude existentes, con cuatro arquitecturas, ocho proveedores candidatos, 16 experimentos propuestos y un notebook ejecutable sobre fallos conjuntos y resiliencia. Las arquitecturas son **diseño S1**; el notebook es **experimento S2 sintético acotado**. No representan integraciones comerciales ni un quinto especialista terminado.

La prioridad es impedir que una evidencia convincente se convierta por sí sola en autorización de crédito o de desembolso. Un rostro coincidente, un documento sin alertas o una sesión autenticada solo resuelven parte de la decisión.

| Material | Uso |
|---|---|
| [Amenazas y 16 ideas](THREATS_AND_EXPERIMENTS.md) | Ataque, hipótesis, baseline, fórmula, datos, prueba y criterio para descartar |
| [Proveedores y selección](PROVIDERS.md) | Ocho candidatos por capacidad; preguntas y evaluación comparables |
| [Arquitecturas y contratos](ARCHITECTURES.md) | Cuatro diseños por capas, fallos, responsables e integración económica |
| [Diagramas editables](diagrams/README.md) | Archivo draw.io con cuatro páginas y cuatro vistas SVG |
| [Notebook](notebook.ipynb) y [resultados](RESULTS.md) | 32 celdas, ecuaciones, tres figuras; dependencia entre controles y colas |
| [Evidencia de ejecución](evidence/execution.json) | Conteos, modo real de ejecución y hash |
| [Fuentes](sources.json) | Fecha, fuente primaria y límites de lo que respalda |

## Qué se está haciendo y qué proponemos

FinCEN documentó el uso sospechado de medios sintéticos y documentación alterada para evadir la verificación financiera [S:fincen]. NIST separa explícitamente la protección de captura y los controles contra medios manipulados [S:nist]. El toolkit de la Reserva Federal reúne recursos para identidad sintética [S:fed]. Son referencias para modelar amenazas; no prueban la eficacia de nuestra arquitectura.

Las soluciones consultadas ofrecen biometría, señales de dispositivo, comportamiento, datos financieros u orquestación. **La combinación propuesta y sus políticas son diseño propio**. Una evaluación de presentación facial no demuestra resistencia a todas las inyecciones; conocer la identidad no descarta coerción, mula ni insolvencia.

## Orden de implementación

1. **Contrato y replay:** preservar corte, disponibilidad, versiones, estado y origen antes de combinar scores. Usar identidades sintéticas en laboratorio, sin documentación de terceros.
2. **Originación e ingresos:** probar una fuente especializada frente al baseline interno, con falsos positivos y carga de revisión comunes.
3. **Sesión y desembolso:** revalidar cambios de beneficiario y señales de toma de cuenta; el KYC inicial no cubre toda la vida de la cuenta.
4. **Red y cambios:** evaluar asociación temporal sin criminalizar hogares, comercios o dispositivos compartidos.
5. **Piloto en sombra:** congelar política, adjudicar muestras aprobadas y alertadas, observar maduración y contrastar costos. Despliegue solo después de validación institucional.

## Conexiones existentes

- [Motor de minimización de pérdida](../loss-minimization-engine/README.md): conserva la asignación bajo capacidad; la eficacia por acción sigue siendo un supuesto.
- [KYC y conformal por canal](../01-identity-kyc-consistency/channel-conformal-audit/): controla alertas bajo sus supuestos, sin transformar p-valores en probabilidades de fraude.
- [Grafo temporal](../02-temporal-application-graphs/), [ingresos](../03-income-document-consistency/) y [proceso](../04-origination-process-anomalies/).
- [Decisiones tipadas y evidencia documental](../../../../05-artificial-intelligence-and-computational-systems/03-deep-learning-and-foundation-models/structured-decision-architectures/): reutilizar contratos, abstención y fidelidad; un span válido no prueba autenticidad ni sustento semántico.

**Separación económica:** fraude, PD/LGD/EAD, coerción y lavado requieren etiquetas y tratamientos distintos. Un ledger de incidentes asignará cada flujo perdido una sola vez. No sumar pérdida de fraude e incumplimiento cuando contienen el mismo saldo.

Los IDs `[S:...]` remiten a [sources.json](sources.json). Disponibilidad, precios, residencia, cobertura documental y requisitos legales locales siguen pendientes de diligencia; no se presenta un ranking ni una recomendación de compra.
