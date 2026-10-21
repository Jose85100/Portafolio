# 02 · Redes temporales de solicitudes y fraude coordinado

**S1 — diseño detallado.** Investigar grupos que comparten infraestructura o destinos de desembolso. La pertenencia a una red no demuestra fraude: hogares, comercios y asesores pueden vincular legítimamente a muchas personas.

## Hipótesis y población

Hipótesis: relaciones temporales aportan detección incremental sobre variables individuales, especialmente cuando cada solicitud parece plausible. Puntuar una nueva solicitud antes del desembolso y crear un caso por grupo investigable, conservando razones por vínculo.

Ejemplo ilustrativo: varias solicitudes recientes usan dispositivos relacionados y convergen en un mismo destino de fondos. El interés está en la combinación, la novedad y la sincronía; compartir una IP pública por sí solo tendrá evidencia débil. Un centro de atención legítimo con equipos compartidos será un control negativo central.

## Grafo y variables

Construir `G_t=(V_t,E_t)` con nodos tipados: solicitud, solicitante tokenizado, dispositivo, teléfono tokenizado, cuenta destino y, cuando proceda, entidad empleadora verificada. Cada arista incluye tipo, confianza, `event_at`, `available_at` y vigencia. La infraestructura de captura solo aporta datos autorizados; no se propone rastrear terceros.

Variables: grado por tipo de entidad en ventanas 1/7/30 días; solicitantes distintos por dispositivo; concentración de destinos; proporción de vínculos nuevos; crecimiento de componente; repetición de pares; sincronía de solicitudes; y vecinos con fraude confirmado **y conocido antes del corte**. Estimar grados esperables dentro de canal, producto y tipo de nodo.

Atenuar hubs compartidos con una ponderación de diseño como `w(u,v)=exp(-(t-t_e)/tau)/log(2+degree_t(v))`. El decaimiento `tau` y las ventanas son hiperparámetros, no constantes universales. Un componente enorme debe investigarse como posible unión errónea por una entidad ubicua antes de tratarse como campaña.

## Escalera de modelos

1. **Reglas:** conteos de reutilización y convergencia de cuentas con razones verificables.
2. **Modelo tabular de grafo:** logit o boosting con variables individuales y agregados temporales. Es el primer challenger por trazabilidad y costo.
3. **Propagación acotada:** experimento con semillas de fraude históricamente disponibles y número fijo de pasos; evaluar contaminación por vecinos legítimos. No traducir proximidad a culpabilidad.
4. **GNN heterogénea temporal:** solo si volumen, etiquetas y conectividad justifican complejidad. Construir mensajes con vecinos disponibles al corte, comparar contra igual información tabular y medir latencia, memoria y casos sin vecinos.

Una forma propuesta de mensaje es `h_i'=phi(h_i, sum_j alpha_ij(t)*psi(h_j,e_ij))`. El aprendizaje y la selección de vecinos no pueden ver aristas futuras ni etiquetas del test. El carácter temporal de una arquitectura por sí solo no garantiza ausencia de fuga.

## Etiquetas, partición y evaluación

Un caso puede confirmar diez solicitudes; contar tanto solicitudes afectadas como campañas distintas. No replicar una etiqueta positiva automáticamente sobre todos los miembros de un componente. Guardar qué vínculos fueron confirmados y cuáles quedaron inconclusos.

Hacer dos pruebas: operación temporal con redes históricas conocidas; y campañas/componentes no vistos. Para la segunda, asignar grupos con un snapshot documentado y excluir grupos que crucen el corte según protocolo; una agrupación retrospectiva puede servir para evaluación, nunca para generar variables disponibles en producción. Declarar pérdida de muestra y posible cambio de población.

Métricas: precisión/recall por caso, cobertura por solicitud, tiempo hasta primera alerta de campaña, pérdida expuesta antes de detectar y alertas duplicadas. Estimar incertidumbre por caso y bloque temporal, no suponiendo solicitudes independientes.

## Experimentos y contraejemplos

- Generar familias, comercios y agencias legítimas con hubs; añadir campañas con vínculos compartidos parcialmente observables.
- Comparar individual vs individual+grafo a igual capacidad. Ablacionar cuenta, dispositivo, contacto y señal de vecinos confirmados.
- Variar rotación de entidades, pérdida de aristas, demora de confirmación y errores de resolución de identidad.
- Inyectar eventos futuros y comprobar invariancia de salidas históricas. Comparar también con un baseline deliberadamente retrospectivo, marcado inválido, para ilustrar inflación por fuga.
- Evaluar componentes grandes y solicitantes nuevos aislados. Reportar cuándo el grafo no puede aportar señal.

La hipótesis se refuta operativamente si el aporte desaparece al separar campañas, si todo depende de etiquetas futuras o si los falsos positivos en hubs legítimos consumen la cola.

## Entregables y pasos

Diseño de entidades y resolución; generador de redes temporales; snapshot reproducible; baseline de conteos; modelo tabular; notebook de campañas no vistas; ficha de latencia y caso exportable con subgrafo explicativo minimizado. No publicar tokens reales ni subgrafos de clientes.

Primero implementar agregados auditables; después decidir si una GNN mejora suficiente para su costo. [CaT-GNN, Duan et al.](https://arxiv.org/abs/2402.14708) es antecedente en fraude transaccional; su arquitectura y sus resultados no validan automáticamente este caso de originación.

## Integración con motores y capas

Este especialista conserva estado S1. Su familia de señal se representa mediante una variable sintética en el [motor S2 de comparación y asignación](../loss-minimization-engine/README.md); ese experimento no implementa el detector especializado descrito arriba. Véanse [capas y contratos](../ARCHITECTURE.md) y [técnicas y función de pérdida](../MODEL_AND_LOSS_METHODS.md) para el desarrollo incremental y los criterios de comparación.
