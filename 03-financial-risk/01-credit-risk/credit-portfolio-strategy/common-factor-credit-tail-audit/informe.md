# CICLO26 de octubre de 2026 — factor común en cartera finita

## 1. Título
PMF finito con dependencia gaussiana y diagnóstico de convergencia de cola.

## 2. Hipótesis y novedad incremental
H1: para granular,rho 0,2,ES99 supera independencia al menos50%. H2: en la cartera granular base rho0,2, los dos últimos órdenes observados superan toleranciasCDF1e−5 yES0,01unidades; oráculo bivariado tiene error≤1e−12. Config fijada antes de ejecutar. Es adaptación local del DP25 con factor y pruebas de integración; no nuevo modelo de crédito o nueva cuadratura.

## 3. Estado del arte
Cinco fuentes primarias verificadas el 26 de octubre: Gordy (un factor y granularidad), Vasicek (límite condicional), Hong (distribuciones deBernoullis), Acerbi/Tasche (ES con átomos) y documentación SciPy (Gauss-Hermite de estadísticos). Referencias BibTeX y registro de alcance en prior-art. Texto completo de Vasicek restringido; se verificaron resumen/metadatos, no se afirma lectura exhaustiva. SciPy online 1.18 vs runtime 1.17 se registra explícitamente.

## 4. Brecha y alternativas
El ciclo 25 mostró que independencia puede fallar enormemente ante shock común. Tres alternativas: discretización de pesos, importance sampling y mezcla por factor. Se selecciona tercera para remediar el supuesto sin modificar el núcleo25. El notebook Vasicek anterior simula una cartera homogénea; aquí se obtiene PMF finito ponderado y diagnóstico de error por órdenes. PR83 documental permanece fuera del alcance.

## 5. Diseño/config
Carteras: granular 100×3 y concentrada 100+20×10, pérdida máxima300,PD 2%,EL6. rho latente0,2 base y0,95 stress. q=.99. GH16/32/64/128 con referenciaGH256. MonteCarlo20semillas0–19 por cartera,20.000draws/semilla, mismoDGP de factor para evitar comparar modelos distintos. CDFtol1e−5 yEStol0,01. Condiciones de estabilidad observadas, no cota de error certificada. Los resultados de stress son diagnóstico negativo, no validación a rho alto.

## 6. Modelo e implementación
Aᵢ=√rhoY+√(1−rho)εᵢ, Y yεᵢ normales independientes. Dᵢ=1[Aᵢ≤Φ⁻¹(pᵢ)]. CondicionandoY=y, pᵢ(y)=Φ((Φ⁻¹(pᵢ)−√rho y)/√(1−rho)). EjecutarDP25 para cada nodo sobre pesos enteros; PMFmezcla=Σaⱼf(l|yⱼ), con aⱼ=wⱼ/√(2π) de roots_hermitenorm. rho es correlación latente, NO correlación de defaults. Parámetrosρ∈[0,1),2..1024 nodos; rho 0 devuelve exactamente kernelindependiente. EndpointsPD0/1 tratados porΦ(±∞). ES se calcula DESPUÉS de mezclar PMF, no promediandoEScondicional. El adaptador carga el archivo hermano sin editar; SHA256 enmetrics. ComplejidadO(KnΣw), memoriaO(Σw) más nodos. No es standalone fuera del repo.

## 7. Tests y benchmark
Cinco tests: rho 0identidad; ortantebivariado conPD.5 yP(ambos)=1/4+asin(rho)/(2π); marginal de una obligaciónPD.02,rho.2; masa/media/permutación/PD0y1; diagnóstico y entradasinválidas. Cobertura medida enresults/coverage, solo src.factor/base: no se afirma cobertura del kernelhermano ni experimento. Ruffsrc/tests/benchmarks y mypyestricto adaptador/factor, scipy sin stubs se excluye de validación estática interna. C++/sanitizers no aplican. Convergence registra tiempo por orden,masa,media,L1 yES vsreferencia. Memoria tracemalloc y tiempo global incluyenDPyMC y overheadinstrumentación, no latencia de producción.

## 8. Resultados ejecutados
|Cartera,rho 0,2|VaRind|ESind|VaRfactorGH256|ESfactorGH256|
|---|---:|---:|---:|---:|
|Granular|18|19,5673099|42|55,2685961|
|Concentrada|100|108|110|120,9811985|
IncrementoES+182,45% y+12,02%. Granular: errorESGH16vsGH2560,0788206;GH32=0,0050506;GH64=8,83e−6;GH128=−6,62e−11. Paso64→128 satisface estabilidadCDF/ES. Error ortante analítico≈1,11e−16. FuenteCSV/JSON y notebookcalculado. No se interpreta GH256 como verdad, solo referencia másfina; tolerancia superada es evidencia numérica local.

## 9. Análisis crítico y caso negativo
rho 0,95 produce VaRgranular96/282/198/258 enGH16/32/64/128, y237 enGH256: oscilación fuerte. ES128−ES256≈−1,170; concentración también falla estabilidad. Masa≈1 puede ocultar errores de media/cola; registrosCSV los exponen. La CDFcondicional se vuelve abrupta conrho alto y GHmoderado pierde resolución. No se reduce la tolerancia para fingir éxito. GH256stress tampoco se certifica. No hay adaptación de orden automática ni extrapolación de convergencia.

## 10. Limitaciones y riesgos
PD/rho conocidos, un factor común, normalidadlatente, LGD/EADfijas y pérdidasenteras son hipótesis. No se estima correlación ni se traslada la cifra a una cartera real. q extremo/PD muy bajas/rho cercano a 1 pueden requerir otros métodos. El diagnóstico puede coincidir entre órdenes y seguir sesgado; no cota de error rigurosa. No hay intervalos sobre parámetros, validación empírica, criterio operativo, provisión ni capital regulatorio. Modelo más rico no equivale a modelo calibrado.

## 11. Reproducción
`bash run.sh` instala versionesdirectas en venv y ejecuta todo. `SKIP_INSTALL=1` reutiliza entorno. Preservar ../discrete-credit-tail-audit/src/loss.py; hashes yversiones enmetrics. Notebook real IPython in-process secuencial con outputs capturados, sin necesidad de ZeroMQ; figura inspeccionada separadamente y no se afirma render HTMLcompleto. Dependencias transitivas sin lock total.

## 12. Referencias
Cinco entradas reales en referencias.bib, incluida fuente oficial de cuadratura; revisión focal no exhaustiva. Derivación condicional consistente con marco existente, sin atribuir nuestras cifras a artículos.

## 13. Rúbrica
Autoevaluación: novedad2/5,rigor4,reproducibilidad4,código4,claridad4,impacto3,honestidad5,MVP4. Componente prototipo sintético; estado de revisión independiente y publicación solo con evidencia posterior. No se eleva dominio/programa.

## 14. Siguiente iteración
Siguiente iteración recomendada: comparar Gauss-Hermite con integración adaptativa para rho alto antes de aceptar cifras de stress. Tareas: common-factor-credit-tail-audit añadir referencia adaptativa independiente; discrete-credit-tail-audit certificar discretización de pesos; risk-engines portar mezcla con pruebas cruzadas y sanitizers.

## Checklist
Código/comando/tests/baseline numérico/CSVJSONfigura/notebook ejecutado/README/informe/cinco referencias/MVP/config/entorno presentes. Revisión independiente/publicación reportadas aparte; no se simulan verificaciones.
