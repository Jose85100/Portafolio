# Contrato de MVP

- **Qué es:** extensión ejecutable de asset-management que corrige la tolerancia numérica
  de mínima varianza y evalúa un filtro de beneficio de riesgo contra costos.
- **Cómo corre:** desde raíz, `bash 04-quant-strategy-and-products/asset-management/rebalanceo-beneficio-costo/reproduce.sh`.
- **Qué produce:** tests y cobertura, 720 backtests con 6 estrategias, 20 seeds,
  2 regímenes y 3 costos; CSV/JSON, figura y notebook ejecutado con IPython en proceso (sin sockets de kernel).
- **Baseline:** pesos iguales, solver diario original, MV estática, MV mensual corregida.
- **Estado:** M2, prototipo verificado por pruebas y simulación; no validación empírica.
- **No cubre:** datos reales, alfa, pricing, órdenes, liquidez, impacto, impuestos,
  dividendos, gobernanza productiva, datos aprobados ni validación independiente.
- Los motores C++ del repo siguen siendo prototipos; no se cambian en este MVP.
- Cierre: código, comando único, tests, baseline numérico, salidas,
  README/informe/referencias/MVP y ubicación correcta presentes.
