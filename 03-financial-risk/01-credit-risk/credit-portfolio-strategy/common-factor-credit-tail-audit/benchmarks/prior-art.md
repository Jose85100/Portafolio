# Selección y revisión focal — 26 de octubre de 2026

Se compararon tres ideas:
1. Cota de error al discretizar pesos reales: reutilizable, pero cambia menos la interpretación económica del ciclo 25.
2. Importance sampling de factor común: útil para pérdidas raras, pero tuning y diagnóstico aumentan alcance.
3. **Seleccionada:** mezcla de distribuciones finitas condicionadas a factor gaussiano y diagnóstico de convergencia. Corrige el supuesto de independencia de25oct sin modificar el kernel auditado.

Se inspeccionó main674699d. PR83 abierto afecta IDEAS_SIMULATIONS/IDEAS_VANGUARDIA: no se usa como integrado ni se modifica. El notebook Vasicek existente usa pérdidas homogéneas y simulación; esta extensión genera PMF heterogéneo ponderado condicionando el DP25 y compara órdenes de integración. No duplica la propuesta documental83.

Cinco fuentes primarias abiertas26oct: Gordy2002Fed (un factor y granularidad); Vasicek2002Risk (metadatos/resumen; texto completo limitado); Hong2011VirginiaTech (Poisson-binomial yDFT, no nuestro método de cuadratura); Acerbi/Tasche2002arXiv (ES y átomos); SciPyAPIroots_hermitenorm (peso exp(-x²/2), nodos/pesos). La documentación online mostraba1.18; runtime1.17 registrado, mismaAPI utilizada. Revisión focal, no exhaustiva. No se reivindica nuevo modelo gaussiano ni error certificado.

Novedad local: adaptar el DP finito existente al factor, verificar el oráculo ortante bivariado y exponer un caso de correlación alta donde sucesivos órdenes no estabilizan aunque masa=1. Ninguna referencia se usa para afirmar cifras de nuestro experimento.
