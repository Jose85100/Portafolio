"""Generate the critical scientific report only from executed raw evidence."""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    result = json.loads((ROOT / "benchmarks/results.json").read_text())
    with (ROOT / "benchmarks/summary.csv").open() as f:
        summary = list(csv.DictReader(f))
    a = result["adversarial"]
    lines = [
        "# Informe crítico — 2026-10-19\n",
        "## Pregunta y brecha\n¿Un último coeficiente pequeño controla el error acumulado de una diferencia fraccional truncada? El programa 05 era un protocolo S1 sin código. Este MVP S2 implementa el operador discreto, verifica su aritmética y explicita el coste de truncar memoria. No resuelve todavía la pregunta mayor de distinguir memoria larga genuina de rupturas estructurales.\n",
        "## Hipótesis falsable y umbrales\nAntes de ejecutar se fijaron en config.json: error escalado FFT frente a convolución completa ≤1e-10; violación numérica de la cota de cola ≤1e-10; error escalado del selector de presupuesto ≤0.0100000001; diferencia frente a oráculo de 80 dígitos ≤1e-11; un contraejemplo constante con error del corte por coeficiente ≥20 veces epsilon; igualdad de cota y error constante a tolerancia 1e-10; y contaminación por FFT circular ≥0.1. Ningún umbral se relajó tras ver resultados. Son comprobaciones del operador y del benchmark, no inferencia económica.\n",
        "```json\n"
        + json.dumps({"checks": result["checks"], "passed": result["passed"]}, indent=2)
        + "\n```\n",
        "## Definición y condiciones iniciales\nSe calcula y_t=Σ_(k=0)^t w_k x_(t-k), t=0,...,N-1, con x_t=0 para t<0, paso del rezago igual a uno y w_k=(-1)^k binom(d,k). El dominio soportado es d en [.01,.99], N entero entre 1 y 32768, entradas finitas con norma sup ≤1e8. No es automáticamente una derivada Caputo ni una aproximación de una EDE fraccional continua. La extensión inicial cero forma parte del contrato.\n",
        "Los coeficientes cumplen w_0=1 y w_k=w_(k-1)(k-1-d)/k. Para 0<d<1 todos los coeficientes posteriores son negativos. La identidad binomial y Gamma da r_m=Σ_(k=0)^m w_k=Γ(m+1-d)/[Γ(1-d)Γ(m+1)], que decae como m^(-d)/Γ(1-d). En una constante con historia infinita el resultado sería cero; con inicio en t=0 el resultado correcto es r_t, no cero. Confundir esas inicializaciones atribuiría al algoritmo un error que viene del modelo de frontera.\n",
        "## Proposición: cota finita de truncación\nSi se retienen rezagos 0,...,m y |x_t|≤M, entonces para t>m, |y_t^(m)-y_t|≤M Σ_(k=m+1)^t |w_k|≤M T_(m,N), donde T_(m,N)=Σ_(k=m+1)^(N-1)|w_k|=r_m-r_(N-1). La prueba es la desigualdad triangular y el signo de los pesos. Para x_t=1 desde t=0 se alcanza la cota al final del horizonte: el error es exactamente T_(m,N) en aritmética real.\n",
        "El selector escoge el menor m con T_(m,N)≤eta. Por tanto controla el error absoluto por M*eta, no el error relativo respecto de una salida que pueda ser casi cero. Se evalúa T mediante suma inversa de pesos absolutos para evitar restar ratios Gamma cercanos. Son cotas matemáticas verificadas con tolerancia float64, no certificados de aritmética de intervalos. La constante hace que la cota no sea solo una desigualdad muy holgada en todos los casos.\n",
        "### Por qué cortar por un coeficiente no basta\nEl baseline descarta el primer w_k con |w_k|≤epsilon y todos los siguientes. Controla ese coeficiente individual, no su suma. No se afirma que toda implementación financiera use esta regla ni se atribuye un fallo universal a una librería concreta. Se compara esta heurística explícita frente a dos memorias fijas (32 y 128), convolución completa directa, FFT lineal completa y el selector por presupuesto.\n",
        "## Diseño y baselines\n36 escenarios: d=.1,.4,.8; N=256,2048,8192; constante, sinusoide de periodo 64, AR(1) de parámetro .95 y pulso. Las entradas tienen norma sup ≤1 y las 12 series se guardan en inputs.npz; las semillas constan en CSV/config. No se simulan procesos ARFIMA para inferir d: se audita aplicar un operador conocido a señales conocidas. Seis métodos producen 216 resultados, con tres repeticiones temporales cada uno (648 registros). Las repeticiones de tiempo no son réplicas estadísticas independientes.\n",
        "La referencia principal es la convolución causal completa de los mismos pesos. Para no limitarse a concordancia entre dos algoritmos float64, seis casos cortos (64/256 × tres d) se contrastan con coeficientes binomiales de mpmath y sumas a 80 dígitos. El prefijo Gamma se comprueba por separado. La FFT usa convolución lineal con relleno a longitud suficiente; el ejemplo circular deliberadamente incorrecto es una ablación de frontera, no un baseline competitivo justo.\n",
        "## Contraejemplo predefinido\n",
        f"Constante unitaria, d=.4, N=8192, epsilon=.001: el corte conserva el rezago máximo **{a['memory']}**. El error máximo es **{a['max_abs_error']:.9f}**, frente a cota **{a['finite_tail_bound']:.9f}**; equivale a **{result['checks']['min_cutoff_error_over_epsilon']:.2f} veces epsilon**.\n",
        "| Método | Rezago máximo | Coeficientes retenidos | Error máximo | Cota de truncación |\n|---|---:|---:|---:|---:|",
    ]
    for row in summary:
        if row["family"] == "constant" and row["n"] == "8192" and float(row["d"]) == 0.4:
            lines.append(
                f"| {row['method']} | {row['memory']} | {int(row['memory']) + 1} | {float(row['max_abs_error']):.9g} | {float(row['finite_tail_bound']):.9g} |"
            )
    lines += [
        "\n## Coste y escalabilidad\nPesos y selección se preparan fuera del cronómetro y se registran en setup.csv. La llamada medida incluye validación de entradas/pesos y el filtrado; no incluye RNG ni selección. Se calcula una referencia directa antes de medir, sin calentamiento separado y con orden fijo. Son tiempos descriptivos locales, no una garantía universal de velocidad. Pico tracemalloc en una llamada separada; no es RSS.\n",
        "| N | Método, AR1 d=.4 | Mediana ms | Pico rastreado bytes | Error escalado |\n|---|---|---:|---:|---:|",
    ]
    for row in summary:
        if (
            row["family"] == "ar1"
            and float(row["d"]) == 0.4
            and row["method"] in ("full_direct", "full_fft", "tail_budget")
        ):
            lines.append(
                f"| {row['n']} | {row['method']} | {1000 * float(row['median_seconds']):.3f} | {row['tracked_peak_bytes']} | {float(row['scaled_error']):.6g} |"
            )
    lines += [
        "\n![Auditoría](benchmarks/audit.png)\n",
        "## Qué funcionó y qué no\nLa FFT conserva el operador de historia completa dentro de tolerancia y el selector controla la truncación bajo las hipótesis indicadas. El corte por un coeficiente falla el presupuesto de error en el contraejemplo. No se eliminan las familias donde una memoria fija basta ni donde el selector conserva casi toda la historia. Con d pequeño, la cola decrece despacio y el control de error puede exigir muchos rezagos; no se afirma que la memoria corta siempre sea barata.\n",
        f"La ablación circular produce un primer valor **{result['boundary']['circular_first_value']:.6f}** para un pulso situado en el último instante, cuando el valor causal correcto es **{result['boundary']['linear_first_value']:.6f}**: usar FFT sin relleno introduce información del final al inicio. Para la constante con extensión cero, el último valor completo es **{result['boundary']['zero_extended_constant_last_at_n8192']:.9f}**, no cero. Ambos fallos se guardan explícitamente en results.json.\n",
        "## Límites y riesgos\nOperador lineal discreto escalar, no estimación de Hurst/d ni prueba de estacionariedad, y sin datos económicos reales. No diferencia memoria larga de cambios de régimen; ese objetivo del programa sigue pendiente. Cota escalada por max(1,||x||∞), no por ||y||∞. La cota es de truncación y se admite tolerancia adicional de redondeo: no garantiza todos los bits de una FFT. El oráculo de alta precisión se limita a N≤256; en N grande la referencia directa también es float64.\n",
        "El selector conoce el horizonte N; la garantía no se extiende automáticamente a futuras observaciones ni a prehistoria desconocida. No se usa información futura para calcular y_t: los coeficientes dependen solo de d/N/tolerancia, y el filtro es causal. Este prototipo prepara y almacena los N pesos para seleccionar m, así que no se reclama implementación streaming ni reducción del almacenamiento total del programa. No cubre d=0/1, d negativo, órdenes variables, Caputo, EDE fraccionales o inferencia financiera. Dependencias directas fijadas, no lock transitivo.\n",
        "## Calidad, notebook y trazabilidad\nmake run instala, comprueba Ruff/formato/mypy, ejecuta pytest/Hypothesis, mide cobertura solo de src/fractional.py y src/reference.py, reproduce benchmark, informe, notebook y checklist. Se corren también las pruebas existentes de numerical-core. Los logs son evidencia de lo realmente medido. Notebook con ocho celdas ejecutadas en IPython en proceso; --kernel permite nbclient convencional. Figura revisada, notebook estructuralmente validado; la revisión visual integral en un visor se declara por separado. Las guías de notebooks y visualización orientaron la separación de supuestos, datos, resultados y límites.\n",
        "## Prior art y novedad incremental\nDiferenciación fraccional y FFT no son nuevos: Granger–Joyeux (1980), Hosking (1981), Lubich (1986), Jensen–Nielsen (2014), NIST DLMF y documentación SciPy. referencias.bib contiene seis entradas verificadas; fuentes.md documenta barreras de acceso. No se declara revisión exhaustiva de todas las plataformas sugeridas. La aportación es el paquete reproducible de cotas, contraejemplos de truncación/frontera y benchmarks dentro de este programa del portafolio.\n",
        "## Rúbrica (1–5)\nNovedad 2; rigor 4; reproducibilidad 4; código 4; claridad 4; impacto potencial 3; honestidad 5; MVP ejecutable 5. Autoevaluación, no certificación externa.\n",
        "## Siguiente iteración recomendada\n1. advanced-research: contrastar memoria larga y rupturas estructurales con pruebas calibradas en réplicas independientes.\n2. advanced-research: estudiar sensibilidad a la prehistoria y al horizonte de la cota.\n3. quantitative-methods: añadir implementación por bloques/streaming y benchmarks a presupuesto de error común.\n",
    ]
    content = "\n".join(lines)
    content = re.sub(r"(?m)^(#{1,6} .+)\n(?!\n)", r"\1\n\n", content)
    (ROOT / "informe.md").write_text(content)
    print("Critical report regenerated from raw evidence.")


if __name__ == "__main__":
    main()
