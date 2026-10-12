# Fundamentos — Advanced AI Systems Engineering

**Fuera del conteo de diez proyectos.**

## I. Matemática y teoría

Álgebra lineal numérica; optimización convexa y no convexa; backpropagation y diferenciación automática; teoría de información; atención y transformers; procesos de Markov y RL; teoría de colas; sistemas distribuidos; lógica formal y complejidad algorítmica.

## II. Estadística y aprendizaje

Generalización, regularización, validación temporal, evaluación pareada, bootstrap, inferencia bayesiana, incertidumbre predictiva, calibración, detección de drift, evaluación off-policy y robustez adversarial. Cada estimador requiere supuestos y diagnóstico de sesgo.

## III. Sistemas computacionales

C++17/20, Python, PyTorch, CUDA/Triton opcionales, memoria CPU/GPU, vectorización, concurrencia, RPC, almacenamiento, colas, Docker, CI/CD, trazabilidad, telemetría y seguridad de herramientas. Benchmarks deben reportar hardware, seeds, warm-up, número de repeticiones y variabilidad.

## IV. Contratos y arquitectura

`ModelArtifact/v1`, `InferenceRequest/v1`, `RunContext/v1`, `EvaluationResult/v1`, `SecurityFinding/v1`. Registrar versión de modelo, tokenizer, hardware, entorno, datos, permisos, presupuesto y resultados. Implementar controles de acceso y políticas de retención.

## V. Gates

S1 diseño falsable → S2 código/tests → S3 benchmarks estadísticos y seguridad → S4 evaluación independiente → S5 operación gobernada. Datos sintéticos o demos no acreditan robustez en producción.
