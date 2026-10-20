# Contrato del MVP — 2026-10-20

Qué es:solver estático de pagos EN y liquidación mínima de un activo,enumerando
regímenes en redes de1–4 bancos. Amplía un componente S2 existente con evidencia;
no eleva el programa completo a S3.

Cómo corre,desde la raíz del repo:

```bash
bash 01-economics-and-econometrics/05-macrofinance/01-sovereign-bank-strategic-nexus/coupled-clearing-audit/reproduce.sh
```

Qué produce:censo de pagos/precios,defaults,ventas,impago externo y bruto,
equity/identidad,residual,comparaciones con cobros congelados y EN condicionado,
tests,cobertura,tiempo,pico de asignación Python,8 CSV,JSON,figura y notebook
ejecutado con outputs. Instrucciones de entorno y dependencias fijadas incluidas.

Qué NO cubre:colateral,préstamos,redes de más de4 bancos,múltiples activos,
quiebra costosa,estrategias óptimas,feedback fiscal,default soberano endógeno,
datos reales,identificación,selección probabilística,bienestar o certificación
formal de todos los errores de redondeo. No se ha validado Docker/Windows.

| Componente | Madurez |
|---|---|
| EN a precio fijo anterior |S2,regresión ejecutada|
| Mercado sin enlaces anterior |S2,regresión ejecutada|
| Acoplamiento EN/precio con1–4 bancos |S2 en este ciclo|
| Colateral,préstamos y múltiples activos |S1|
| Juego fiscal y gobierno estratégico |S1|
| Identificación/validación empírica |S1,no ejecutadas|
| Programa completo |S2 parcial,no S3/S4|

Checklist de cierre:[x]src ejecutable;[x]comando único;[x]test pasa;
[x]baseline numérico;[x]salida guardada;[x]README/informe/referencias/MVP;
[x]05-macrofinance correcta;[x]madurez declarada.

Las hipótesis solo se marcan contrastadas tras ejecución; los tests son de
implementación y escenarios sintéticos,no evidencia financiera observacional.
