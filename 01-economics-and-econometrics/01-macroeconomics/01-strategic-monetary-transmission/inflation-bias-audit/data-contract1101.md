# Contrato de datos — fixture sintética, no validación macro

- Unidad: shock normalizado por período; μ de generación0, varianza declarada; no puntos porcentuales calibrados.
- Dato crudo: `results/estimated-shocks.csv.gz`, CSV sin pérdida: sample_id,time,shock. mtimeGZIP0 para reproducción; SHA256 y versiones en JSON.
- Orden temporal: cada sample_id tiene t1..n observables al decidir t=n+1. La varianza futura se guarda solo como truth de evaluación y jamás se pasa a función del intervalo ni selector q.
- Procedencia/licencia: generador de este repositorio mediante numpyPCG64 y seeds fijadas, sin dataset externo ni recolección. Licencia de repositorio aplicable a fixtures generadas; verificar permisos antes de cualquier dato real.
- Esquema: muestra finita1D,n≥2; confidence entre0,5y0,99; API previa asume v∈[0,16]. Intersección vacía produce abstención. Valores no finitos/varianza desbordada producen ValueError.
- Para datos reales aún falta: fuente oficial/licencia/vintage, definición observable de shock, hash del extracto, publication/availabilitytime, frecuencia/unidades, limpieza, modelo que identifica shocks/α y splittemporal fijado. No interpretar esta fixture como satisfacción de ese contrato empírico.
