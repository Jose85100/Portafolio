# Informe crítico — 2026-10-17

Pregunta: ¿calibración conforme por grupo reduce el fallo de cobertura del segmento ruidoso frente a split global al cambiar la mezcla de segmentos?

Protocolo: 30 semillas pareadas, 4 regímenes (stable, mixture_shift, conditional_shift, rare_group), train/cal/test 400/400/800, alpha=.10. OLS entrenado solo en train. Ruido sigma0=.5, sigma1=2.5; conditional_shift multiplica sigma1 de test por 1.7. Comparación global vs grupo, 240 observaciones experimentales. La rama compacta difiere del ZIP local ampliado (480 evaluaciones, cuatro métodos).

Resultado esperado a refutar: mayor cobertura del grupo peor atendido bajo cambio de mezcla. Las corridas locales del paquete ampliado mostraron global .596 frente a grupo .884 de cobertura del peor grupo bajo mixture_shift; bajo conditional_shift grupo cae a .682. La versión compacta requiere ejecutar reproduce.sh para generar su evidencia exacta.

Ablación negativa: con grupo escaso (<25 observaciones calibración), fallback global no ofrece garantía condicional y puede degradar cobertura. Sin intercambiabilidad de Y|X,G, ninguna garantía universal se conserva.

Limitaciones: sintético, sin datos reales, sin seguridad, privacidad, evaluación independiente ni control de drift operacional. No es modelo productivo. Referencias verificables en referencias.bib.
