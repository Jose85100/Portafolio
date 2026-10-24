# Cuatro arquitecturas de defensa y sus contratos

Son responsabilidades lógicas; no requieren convertir cada caja en un microservicio. [draw.io editable y vistas](diagrams/README.md). Azul identifica componentes internos propuestos; violeta, integraciones externas candidatas; ámbar, estados/revisión. Todas las flechas son intercambios de datos o decisiones; **ninguna significa integración ya desplegada**.

## A. Originación y KYC ante fraude con IA

Separar captura confiable, documento, rostro e identidad entre fuentes. Después integrar cobertura y contradicciones con un modelo temporal fuera de muestra. Una ausencia de señal produce `unavailable`, `inconclusive` o `pending`, nunca una probabilidad cero. La autenticidad de cada medio y el vínculo entre persona/documento son problemas diferentes.

| Capa | Entrada → salida | Responsable / fallo que controla |
|---|---|---|
| Captura | Solicitud y consentimiento → sesión, nonce, referencias de evidencia | Seguridad/canales: replay y sustitución de sesión |
| Verificación | Capturas → autenticidad documental, vida, integridad y estado por control | Identidad: aprobación basada solo en rostro parecido |
| Consistencia | Verificaciones + fuentes al corte → contradicciones y cobertura | Riesgo de fraude: duplicación de la misma evidencia |
| Política | Estimación calibrada + costo/capacidad → continuar/verificar/revisar | Motor económico: sobrecarga y fricción desproporcionada |
| Resolución | Nueva evidencia → decisión y etiqueta versionada | Operaciones: adjudicación separada de la alerta inicial |

Amenazas de referencia: FinCEN [S:fincen] y controles de captura/inyección/medios de NIST §3.14 [S:nist]. Diseño propio: no adopta una obligación local ni afirma conformidad NIST.

## B. Documentos e ingresos con evidencia rastreable

Recibir archivos en zona aislada; conservar original y hash; OCR/LLM produce candidatos con página y coordenadas, **sin herramientas de aprobación ni pagos**. Conciliar titular, período, moneda, concepto, saldo y flujos con fuentes independientes. Los datos de un documento son contenido no confiable, incluidas instrucciones dirigidas al modelo. La extracción no puede modificar política, herramienta ni cuenta destino.

El pipeline de evidencia de IA existente verifica fidelidad literal, no autenticidad. La nueva capa exige pruebas de soporte semántico y conciliación: un abono puede ser un préstamo o transferencia propia. Datos financieros externos [S:belvo-doc] dependen de cobertura e histórico; un archivo ausente no demuestra fraude. Resultado: respaldo suficiente, contradicción verificable o evidencia insuficiente.

## C. Sesión, coerción y desembolso

La identidad inicial no protege cada cambio de beneficiario. Correlacionar autenticación, dispositivo, comportamiento, antigüedad del beneficiario y flujo de dinero. Las señales conductuales comerciales [S:biocatch] y la orquestación [S:feedzai] son candidatos. Un usuario legítimo puede estar bajo coerción; una autenticación correcta no equivale a intención libre.

La política propone verificación adicional, contacto por canal previamente confiable o retención temporal conforme a la política institucional. Un responsable de pagos conserva la autorización. Una comprobación final valida titularidad/destino, versión de política y vigencia de evidencia inmediatamente antes de ejecutar. Vincular `decision_id` con `effect_id`; una restricción única transaccional impide dos efectos con la misma clave. Un evento tardío puede abrir investigación, pero no reescribir la decisión histórica.

## D. Redes, etiquetas y vigilancia de modelos

Un almacén de eventos bitemporal genera grafos al corte; separar IP compartida, dispositivo, domicilio y cuenta receptora. Conteos temporales y motivos son baseline. GNN es challenger, con vecinos disponibles al corte y prueba de enlaces benignos/camuflaje. CARE-GNN [S:care] inspira investigación de camuflaje, no una promesa de desempeño local.

Adjudicar muestras de aprobados y alertados para medir sesgo de selección. El monitoreo compara calidad/cobertura, tasas ajustadas por mezcla, pérdida madura, drift y efecto de cambios de proveedor. Un disparo abre diagnóstico; la liberación requiere evaluación temporal y rollback. No reentrenar automáticamente con toda alerta como fraude confirmado.

## Contrato mínimo de evidencia

```json
{
  "case_id": "synthetic-case-001",
  "request_id": "req-001",
  "event_time": "2026-10-23T10:00:00Z",
  "available_time": "2026-10-23T10:00:02Z",
  "source_id": "document-original",
  "evidence_ref": "restricted://case/evidence",
  "source_hash": "sha256:<computed-from-original-bytes>",
  "provider": "internal-or-candidate",
  "provider_version": "explicit-version-or-unknown",
  "signal_type": "document_authenticity",
  "status": "inconclusive",
  "score_kind": "vendor_score_not_probability",
  "score": null,
  "reason_codes": ["insufficient_quality"],
  "policy_version": "research-v1"
}
```

Ejemplo de contrato, no payload aceptado por una API. Versionar esquema, zona horaria UTC, moneda y horizonte; validar firmas/webhooks conforme a cada proveedor y no registrar medios sensibles en logs generales. El snapshot incluye solo eventos con `event_time <= cutoff` y `available_time <= cutoff`. Usar hash para integridad posterior: no prueba origen verdadero. El nonce enlaza sesión/caso, no autentica por sí mismo una cámara.

Estados terminales y transitorios separados: `passed`, `failed`, `inconclusive`, `unavailable`, `pending`. Solo `passed` significa que ese control produjo una verificación favorable dentro de su alcance. Las transiciones deben conservar historial; un cambio remoto de score no altera retroactivamente la autorización.

## Pérdida, fraude y riesgo crediticio

Para cada caso i y acción a, conservar el contrato del motor existente:

\[
C_{ia}=p_i L_i(1-q_{ia})+c_{ia}+(1-p_i)f_{ia}.
\]

`p`: probabilidad calibrada de fraude para el horizonte; `L`: pérdida condicionada a fraude en moneda común; `q`: eficacia de la intervención, supuesto hasta estimación causal; `c`: costo directo; `f`: fricción monetizada en legítimos. La falta de datos no permite inventar `p`. Con acciones discretas:

\[
\min_x\sum_{i,a}C_{ia}x_{ia},\quad
\sum_a x_{ia}=1,\quad\sum_{i,a}t_{ia}x_{ia}\le B,\quad x_{ia}\in\{0,1\}.
\]

El motor actual ya implementa asignación y escenarios finitos. Añadir espera, múltiples recursos o información futura requiere extenderlo y validarlo; estos diagramas no lo implementan. Bajo escenarios s, comparar `min_x max_s Σ C_ia(s)x_ia` con la política esperada, conservando factibilidad y el mismo menú.

Una partición mutuamente excluyente de eventos permite evitar doble conteo. Por ejemplo, con F=fraude durante el horizonte, D=default de crédito en ausencia de F y pérdida crediticia condicional separada:

\[
\mathbb E[L_{total}]=P(F)\mathbb E[L_F\mid F]
+(1-P(F))P(D\mid\neg F)\mathbb E[LGD\cdot EAD\mid D,\neg F].
\]

Esta identidad no es una fórmula IFRS 9 ni un estimador nuevo; exige esa definición excluyente, horizonte común y no factoriza LGD/EAD sin supuestos. Si hay eventos superpuestos, registrar flujos y atribución en ledger en vez de sumar estimaciones que ya contienen el mismo saldo.

## Fallos y responsables

| Evento | Ruta propuesta | Dueño y evidencia de recuperación |
|---|---|---|
| Timeout de identidad | Estado unavailable, reintento acotado y ruta alternativa; sin aprobación implícita | Canales: deadline/retry/idempotency |
| Caída compartida | Conservar capacidad, priorizar por costo y habilitar política degradada previamente evaluada | Operaciones: replay del incidente y backlog |
| Documento con instrucciones | Tratar texto como datos, extracción sin permisos y validación de esquema/soporte | IA/seguridad: corpus de inyección defensiva |
| Picos de alertas | Presupuesto de revisión y plazo; escalar capacidad solo con responsable | Fraude: minutos, demoras, abandonos |
| Score cambia sin aviso | Etiquetar versión desconocida, alerta de distribución y sombra antes de recalibrar | MLOps: comparación congelada y rollback |
| Sesgo por canal/dispositivo | Medir genuinos excluidos, cobertura y alternativa accesible | Riesgo/modelos: métricas por segmento y apelación |
| Confusión fraude/AML | Un caso con tipologías y colas separadas, derivación al área competente | Cumplimiento: adjudicación y trazabilidad |

## Riesgos vecinos y frontera

Crédito: capacidad de pago y default legítimo. Operacional: caída, doble efecto y sobrecarga. Ciberseguridad: ATO, sesión y credenciales. Conducta: coerción, fricción y exclusión. Modelo: calibración y cambio de población. Privacidad: biometría/PII y retención. AML: mulas y flujo sospechoso. Cada uno necesita métricas, responsables y validación propia; el motor de fraude no reemplaza esos programas.
