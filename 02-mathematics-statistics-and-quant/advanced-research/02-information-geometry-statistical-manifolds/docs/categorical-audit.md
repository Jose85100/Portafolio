# Informe crítico — 2026-10-20

## Pregunta y brecha
¿Fisher–Rao aporta detecciones distintas de Hellinger bajo las mismas permutaciones categóricas?
El programa 02 solo tenía protocolo S1. Ahora contiene un MVP S2 de geometría y contraste de dos muestras.
La pregunta amplia original sobre cambios invisibles no se presume resuelta: en esta familia, la relación
monótona con Hellinger impide ganar potencia solo cambiando el nombre de la distancia.

## Hipótesis falsable y umbrales fijados en config.json
Siete comprobaciones anteriores al experimento: diferencia máxima de p-valores FR/H ≤1e-12;
error absoluto del oráculo ≤1e-11; error de velocidad geodésica ≤1e-10; identidad FR/H ≤1e-12;
error relativo del cuadrático local para paso 1e-6 ≤.01; asimetría del contraejemplo ≥3;
exceso del cuadrático sobre pi ≥.1. No se exige superioridad de potencia frente a Pearson.
Se conservan todas las tasas y resultados negativos.

```json
{
  "checks": {
    "max_pvalue_difference": 0.0,
    "max_oracle_error": 1.1102230246251565e-16,
    "max_geodesic_error": 2.482534153247273e-16,
    "max_identity_error": 2.220446049250313e-16,
    "max_local_smallstep_relative_error": 1.2126111870403022e-05,
    "min_local_asymmetry": 3.944685294770139,
    "min_local_exceeds_pi": 1.783092641180346
  },
  "passed": {
    "max_pvalue_difference": true,
    "max_oracle_error": true,
    "max_geodesic_error": true,
    "max_identity_error": true,
    "max_local_smallstep_relative_error": true,
    "min_local_asymmetry": true,
    "min_local_exceeds_pi": true
  }
}
```

## Modelo, proposición y demostración
Sea p en el interior del simplex de K categorías, K≥2. Para un vector tangente v con suma cero,
la métrica Fisher por UNA observación categórica es g_p(v,v)=sum(v_i²/p_i).
La transformación z_i=2 sqrt(p_i) lleva esta métrica a la esfera de radio 2 en el ortante positivo:
sum(dz_i²)=sum(dp_i²/p_i). Por tanto d_FR(p,q)=2 acos(sum sqrt(p_i q_i)).
Se usa su extensión continua a la frontera cerrada, no una matriz Fisher regular con ceros.

Definiendo H=||sqrt(p)-sqrt(q)||_2/sqrt(2), la identidad de la cuerda da
d_FR=4 asin(H/sqrt(2)), que es estrictamente creciente en H para H en [0,1].
En consecuencia, con las MISMAS particiones, vocabulario, estimador y tratamiento de empates,
cada comparación de cola del test es la misma: los p-valores y decisiones coinciden en aritmética exacta.
Es un hecho matemático conocido, no una equivalencia descubierta por esta simulación.
El test numérico comprueba la implementación; no demuestra una hipótesis de igualdad poblacional a partir de no rechazar.

La geodésica se calcula elevando al cuadrado la interpolación esférica de sqrt(p),sqrt(q).
Se comprueba suma uno, no negatividad y d_FR(p,gamma(t))=t*d_FR(p,q).
La aproximación local sqrt(sum((q_i-p_i)²/p_i)) sirve para desplazamientos pequeños en el interior;
no es simétrica ni una distancia global. Los pesos del modelo multinomial con tamaño n fijo introducirían
un factor sqrt(n): aquí no se usa ese escalamiento para comparar tamaños muestrales.

## Diseño, datos, seeds y baselines
K=8/32, n=m=100/500, cuatro escenarios (nulo uniforme, nulo disperso, desplazamiento denso,
desplazamiento de categoría rara), 100 datasets independientes por escenario: 1.600 datasets.
Cada uno usa 199 particiones uniformes de etiquetas de tamaño fijo condicionadas a los conteos combinados,
muestreadas mediante hipergeométrica multivariante. Se guardan los 318.400 sorteos mediante sus semillas,
no sus matrices completas; counts.npz conserva los 1.600 pares observados, con padding explícito a K=32.
distributions.json conserva las probabilidades poblacionales y replicates.csv todas las semillas.

Se computan FR, Hellinger y Pearson con las mismas particiones; Pearson asintótico sin corrección
es un baseline adicional, no el único competidor. p=(1+# estadísticas permutadas >= observada)/(B+1);
nunca cero, resolución .005. Tolerancia conservadora de empates 1e-12*max(1,|estadística|).
La igualdad exacta teórica de órdenes puede tener excepciones numéricas cerca de empates bajo diferentes
escalas/tolerancias: el gate verifica lo observado, no promete igualdad bit a bit para cualquier entrada.

IID y misma ley bajo H0 implican intercambio de etiquetas. Dependencia temporal, selección del binning
con los datos, vocabularios distintos y cambios de composición no están cubiertos.
No hay datos financieros reales ni calibración para alertas repetidas.

## Resultados: K=32, n=m=100
Fracción de rechazo a alpha=.05; corchetes = intervalo Wilson 95% entre 100 datasets, no bandas simultáneas.

| Método | Nulo disperso | Cambio raro |
|---|---:|---:|
| p_fr | 0.050 [0.022, 0.112] | 0.280 [0.201, 0.375] |
| p_hellinger | 0.050 [0.022, 0.112] | 0.280 [0.201, 0.375] |
| p_pearson | 0.050 [0.022, 0.112] | 0.300 [0.219, 0.396] |
| p_pearson_asymptotic | 0.000 [0.000, 0.037] | 0.030 [0.010, 0.085] |

No se interpreta un solo intervalo ni 100 réplicas como garantía de tamaño exacto empírico.
Los 16 escenarios completos y sus 64 tasas están en summary.csv; no se seleccionó solo el favorable.

## Contraejemplo de distancia local
p=(.99,.01), q=(.5,.5):
FR=1.37046148447, H=0.475107311992,
cuadrático en p=4.92468529477, cuadrático en q=0.98.
El primero supera el diámetro pi de la geometría categórica; cambiar el origen cambia el valor.
Eso refuta interpretarlo como distancia geodésica global, no invalida su expansión local.
El kernel por cuerda evita la resta de una afinidad casi uno; oracle.csv registra también la fórmula
acos ingenua, incluso sus ceros o errores cerca de p=q. No se eliminan esos fallos.

## Benchmarks, precisión y recursos
75 mediciones: K=8,32,128,512,2048 × tres funciones × cinco repeticiones. Entrada fuera de cronómetro,
una llamada de calentamiento por función/tamaño; validación y normalización de probabilidades incluidas.
Métodos en orden fijo. Pico tracemalloc en llamada separada, no RSS; no se afirma velocidad universal.
El tiempo de cada test en replicates.csv incluye sorteos y los cuatro p-valores CON tracemalloc activo;
no es comparable directamente al microbenchmark sin tracing, ni desglosable por test.

Oráculo mpmath 80 dígitos en 12 pares (K=2/8/32; cuatro tamaños de cambio), usando ángulo/afinidad
y normalización de alta precisión. La referencia no repite la fórmula de la cuerda.
Se guardan 132 puntos geodésicos. Todas son comprobaciones float64 con tolerancia, no intervalos certificados.

Hardware registrado: {"platform": "Linux-6.18.55-x86_64-with-glibc2.39", "processor": "x86_64", "machine": "x86_64", "python": "3.12.14"}.
Dependencias directas fijadas; transitivas resueltas en environment.txt, no lock completo.

![Auditoría](benchmarks/audit.png)

## Qué funcionó, qué no y riesgos
El operador es estable y las geodésicas satisfacen los controles. La supuesta ventaja exclusiva
FR frente a Hellinger no existe en el experimento emparejado ni en el argumento de monotonía.
Pearson permutado sigue siendo un baseline legítimo con distinta estadística y puede diferir en potencia.
No se declara que Pearson asintótico falle siempre ni que la geometría supere métodos convencionales.
Ceros empíricos no demuestran categorías imposibles; no se añaden pseudoconteos silenciosos.

## Calidad y presentación
make run instala y ejecuta Ruff, formato, mypy y pytest/Hypothesis; mide cobertura de los tres módulos
numéricos, no del pipeline entero; también corre las ocho pruebas existentes de numerical-core.
El notebook ejecuta seis celdas reales en IPython y puede ejecutarse con --kernel.
La figura se inspecciona por separado; no se afirma inspección visual integral en visor.
Para completar esa revisión abrir notebook.ipynb en Jupyter o exportar a HTML con nbconvert.
Las guías de notebooks y visualización orientaron la separación de evidencia, supuestos y límites.

## Prior art y novedad incremental
Miyamoto y colaboradores (arXiv 2304.14885v3), Lafferty–Lebanon (JMLR 2005),
Phipson–Smyth (2010), Hemerik–Goeman (arXiv 1411.7565v3) y SciPy 1.17.0.
referencias.bib contiene cinco entradas verificadas. fuentes.md documenta alcance de consulta.
No se declara algoritmo nuevo ni revisión exhaustiva de todas las plataformas sugeridas.
Aporte: implementación auditable, contraprueba de ganancia de potencia por reparametrizar la distancia,
referencia independiente y comparación justa a idénticas particiones.

## Rúbrica 1–5
Novedad 2; rigor 4; reproducibilidad 4; código 4; claridad 4; impacto 3; honestidad 5; MVP ejecutable 5.

## Siguiente iteración recomendada
1. advanced-research: categorías aprendidas en entrenamiento independiente y sensibilidad al binning.
2. advanced-research: permutaciones por bloques para dependencia temporal y calibración bajo H0.
3. quantitative-methods: ampliar réplicas y comparar potencia a presupuesto de tiempo común.
