"""Generate the critical report from executed evidence, never from assumptions."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    result = json.loads((ROOT / "benchmarks/results.json").read_text())
    with (ROOT / "benchmarks/summary.csv").open() as f:
        summary = list(csv.DictReader(f))
    with (ROOT / "benchmarks/discretization.csv").open() as f:
        raw = list(csv.DictReader(f))
    lines = [
        "# Informe crítico — 2026-10-17\n",
        "## Tema y pregunta\n¿Puede el aumento de ruido imitar la señal de varianza de una pérdida de recuperación y puede Euler distorsionar estos indicadores OU?\n",
        "## Brecha y alcance S2\nEl programa 01 solo tenía protocolo S1. Ahora tiene una auditoría OU ejecutable; NO se valida el detector no lineal completo descrito en el protocolo original. La revisión encontró métodos y advertencias conocidos; la novedad es integración verificable en el portafolio, no un algoritmo nuevo. No es una revisión sistemática ni exhaustiva.\n",
        "## Hipótesis falsable y umbrales fijados en config.json\nTransición exacta versus exponencial matricial independiente: error escalado ≤1e-12. Emparejamiento de varianzas poblacionales: error ≤1e-12. Error Monte Carlo del segundo momento exacto: |z|≤6 usando SE gaussiano conocido. Euler en κΔt=1: sesgo relativo ≥0.99. Separación poblacional de φ al nivel 0.1: ≥0.5. No se modificaron los umbrales tras ejecutar. El criterio z es una comprobación de ejecución, no una prueba de calibración general.\n",
        "```json\n"
        + json.dumps({"checks": result["checks"], "passed": result["passed"]}, indent=2)
        + "\n```\n",
        "## Formalización y supuestos\nPara κ>0 y ruido blanco aditivo, la solución lineal existe y su transición es X(t+h)=exp(-κh)X(t)+ε, con ε gaussiano independiente de varianza σ²(1-exp(-2κh))/(2κ). La varianza estacionaria es σ²/(2κ). Euler induce AR(1) con a=1-κh y q=σ²h: si 0<κh<2, V_E=σ²/[κ(2-κh)] y V_E/V_OU=1/(1-κh/2). La recurrencia V(n+1)=a²V(n)+q permite evaluar también casos sin estacionariedad. El test de semigrupo y el oráculo matricial validan la implementación, no sustituyen una demostración formal en aritmética exacta.\n",
        "### Contraejemplo de identificación\nA: κ=level, σ=1. B: κ=1, σ=sqrt(1/level). Ambos tienen V=1/(2 level), pero sus correlaciones son exp(-level*h) y exp(-h). Por tanto, el indicador poblacional V no identifica κ sin controlar σ. Esto NO significa que la distribución conjunta temporal sea idéntica: la información serial sí distingue los dos modelos OU especificados. Son episodios estacionarios con 200 réplicas independientes dentro de cada celda y Gaussianas emparejadas entre mecanismos, no una trayectoria con bifurcación o cambio continuo.\n",
        "## Diseño y evidencia\n84 corridas temporizadas, 3,200 episodios estacionarios y 20 comparaciones con exponencial matricial. Configuración, semillas y versiones guardadas; mismos pasos, h, número de trayectorias e innovaciones normales para ambos esquemas. El horizonte 40h varía entre h, no entre métodos del mismo escenario. X0=0 en discretización; X0 estacionario en identificación, sin burn-in. No selección por colapso. El baseline Euler fino h=0.05 está incluido; las inestabilidades de h≥2 son estrés deliberado, no una comparación de precisión a presupuesto equivalente.\n",
        "## Resultados estadísticos al nivel 0.1\n| Mecanismo | Longitud | Mediana segundo momento | Mediana phi | Mediana kappa válida | Tasas indefinidas |\n|---|---:|---:|---:|---:|---:|",
    ]
    for r in summary:
        if r["level"] == "0.1":
            lines.append(
                f"| {r['family']} | {r['length']} | {float(r['variance_median']):.6f} | {float(r['phi_median']):.6f} | {float(r['kappa_median_valid_only']):.6f} | {r['undefined_rate_count']} |"
            )
    lines += [
        f"\nTasas logarítmicas indefinidas totales: **{result['undefined_rates']}** de 3200. Se guardan como campo vacío y se cuentan; las medianas de kappa son solo de tasas válidas. No se recortan coeficientes a [0,1]. El segundo momento usa media cero conocida; no se interpreta como varianza muestral insesgada con media estimada.\n",
        "## Tiempo, memoria y escalabilidad\nMedianas sobre tres semillas, 40 pasos. Memoria: pico rastreado por tracemalloc, NO RSS total; medición separada de tiempo. Orden fijo exacto→Euler y sin warm-up, por lo que NO se reclama superioridad universal de velocidad.\n",
        "| h | Trayectorias | Método | Tiempo mediano ms | Pico rastreado mediano bytes | Error relativo esperado vs OU |\n|---|---:|---|---:|---:|---:|",
    ]
    import statistics

    for h in (0.05, 1.0, 2.5):
        for n in (1000, 10000):
            for method in ("exact", "euler"):
                subset = [
                    r for r in raw if float(r["dt"]) == h and int(r["paths"]) == n and r["method"] == method
                ]
                lines.append(
                    f"| {h} | {n} | {method} | {1000 * statistics.median(float(r['seconds_including_rng']) for r in subset):.3f} | {statistics.median(int(r['tracked_peak_bytes']) for r in subset):.0f} | {float(subset[0]['scheme_relative_bias']):.6g} |"
                )
    lines += [
        "\n![Auditoría](benchmarks/audit.png)\n",
        "## Qué funcionó, qué no y por qué\nEl generador exacto evita el sesgo de discretización de momentos OU. No elimina variabilidad Monte Carlo ni sesgo de estimación finita. La varianza falla como identificador aislado por construcción algebraica; la correlación funciona bajo estos supuestos y muestra dispersión entre réplicas. Euler con κh=1 duplica la varianza estacionaria y con κh≥2 carece de ley estacionaria aunque la EDE continua sea estable. Esos casos negativos permanecen en el CSV. No se descartan trayectorias ni escenarios que contradigan una narrativa de mejora. La aproximación Euler es razonable para pasos pequeños; aquí se muestra también ese control.\n",
        "## Limitaciones y riesgos\nModelo lineal gaussiano escalar, media conocida, observación regular sin error y parámetros constantes dentro de cada episodio. No hay transición crítica simulada: κ permanece positivo. Correlación de ruido, cambio de media, estacionalidad y errores de observación pueden volver insuficiente el diagnóstico serial; no se evaluaron. No hay umbrales de alarma aprendidos, ROC, anticipación, CUSUM ni ajuste fuera de muestra: no se afirma mejora predictiva. Soporte float64 acotado explícitamente en src/ou.py. El oráculo Van Loan tiene dominio más pequeño para evitar desbordamiento de la exponencial por bloques. Dependencias directas fijadas, sin lock transitivo. No se valida provisión, capital, IFRS9 ni decisiones crediticias.\n",
        "## Tests y calidad\nComando: make run (incluye Ruff, mypy y pytest). benchmarks/tests.txt y coverage.json registran tests y cobertura de src/ou.py y src/reference.py, no de toda la aplicación. Hypothesis prueba semigrupo e identidad estacionaria con ejemplos deterministas; los casos límite incluyen ruido cero, paso pequeño, inestabilidad y tasas estimadas indefinidas. El notebook se ejecuta realmente con IPython en proceso y conserva cuatro celdas de código con salidas. La primera ejecución nbclient falló por sockets locales restringidos; no se simula como exitosa. La opción --kernel usa nbclient en entornos convencionales; CI Notebook Reliability lo ejecuta por separado.\n",
        "## Referencias y revisión\nSe verificaron registros primarios de Uhlenbeck–Ornstein (1930), Higham (2001), Van Loan (1978), Scheffer et al. (2009), Dakos et al. (2012) y Boettiger–Hastings (2012). Ver referencias.bib y fuentes.md. La advertencia sobre sesgo de selección motiva no condicionar por colapso; no se replica ese artículo completo.\n",
        "## Rúbrica (1–5)\nNovedad 2; rigor 4; reproducibilidad 4; código 4; claridad 4; impacto potencial 3; honestidad 5; MVP ejecutable 5. Son valoraciones propias, no certificación externa.\n",
        "## Siguiente iteración recomendada\n1. advanced-research: añadir ruido de observación y forzamiento coloreado.\n2. advanced-research: comparar contra CUSUM y un baseline de tendencia con falsas alarmas calibradas en réplicas independientes.\n3. quantitative-methods: añadir discretización exacta multivariante y comparación a presupuesto temporal equivalente.\n",
    ]
    (ROOT / "informe.md").write_text("\n".join(lines))
    print("Report regenerated from saved raw evidence.")


if __name__ == "__main__":
    main()
