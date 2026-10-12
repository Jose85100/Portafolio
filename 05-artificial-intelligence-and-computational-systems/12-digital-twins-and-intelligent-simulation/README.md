# Digital Twins & Intelligent Simulation

**Nueva sección independiente** de Artificial Intelligence & Computational Systems. Esta carpeta es una **plataforma de fundamentos y arquitectura**, no un proyecto terminado ni un número arbitrario de gemelos implementados.

## Misión

Construir sistemas que vinculen observaciones de un sistema físico, económico, financiero u operacional con un estado latente, un simulador, mecanismos de actualización y un motor de decisiones contrafactuales. Diferenciar gemelo sincronizado de una simulación estática.

## Tres fundamentos

1. [Matemática de gemelos y dinámica](fundamentals/01-mathematical-foundations.md)
2. [Inferencia, asimilación y validación](fundamentals/02-statistical-foundations.md)
3. [Arquitectura computacional](fundamentals/03-computational-foundations.md)

## Arquitectura común

[Arquitectura y contratos](ARCHITECTURE.md).

## Líneas de gemelos futuras (no implementadas)

- **Credit & Portfolio Twin:** estados de cartera, PD/LGD/EAD, migraciones y política de cobranza; [propuesta de riesgo preexistente](../../03-financial-risk/04-advanced-research/02-nonstationary-credit-digital-twin/README.md) (ruta relativa desde la raíz del repositorio; consultar allí directamente).
- **Macroeconomic Twin:** transmisión de shocks, nowcasting y escenarios estructurales.
- **Operational Resilience Twin:** redes de dependencias, fallas, tiempos de recuperación y control.
- **AI Infrastructure Twin:** colas, latencia, cargas, costos y resiliencia de agentes/modelos.
- **Market & Liquidity Twin:** posiciones, flujos, shocks de mercado y feedback de liquidez.

Estas son **líneas de evolución**, no cinco proyectos formalmente añadidos. Cada gemelo futuro deberá tener su carpeta, contratos, código, tests y validación.
