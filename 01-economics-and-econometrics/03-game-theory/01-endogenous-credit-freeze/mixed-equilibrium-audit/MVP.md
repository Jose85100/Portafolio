# Contrato de MVP

**Qué es:** extensión del auditor puro a equilibrios bayesianos aislados en
estrategias mixtas de comportamiento, con certificación de incentivos por tipo.

**Cómo corre**, desde raíz:

```bash
bash 01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/mixed-equilibrium-audit/reproduce.sh
```

**Qué produce:** CSV de equilibrios/probabilidades/payoffs/regret, comparación
pura, validación racional, sensibilidad, tolerancias, costos, JSON, figura,
notebook ejecutado y logs de tests/cobertura.

**Qué NO cubre:** parametrización de familias degeneradas, juego global
continuo, estimación estructural, datos reales, selección endógena, dinámica
económica ni recomendación de política. Los soportes singulares factibles
producen rechazo explícito, no éxito parcial silencioso.

**Madurez:** extensión S2 del componente finito de Endogenous Credit Freeze;
resto del programa parcialmente S1. No se declara S3 o S4.

## Checklist

- [x] Código real modular en src/.
- [x] Comando único documentado para instalar y reproducir.
- [x] Tests ejecutados que pasan; cobertura medida en results/coverage.txt.
- [x] Baseline del repo comparado numéricamente.
- [x] CSV/JSON/figura producidos por ejecución.
- [x] README, informe, referencias y MVP.
- [x] Subcarpeta original de 03-game-theory.
- [x] Madurez y alcance reducido declarados.

El checklist se confirma en el cierre del ciclo, no sólo por la existencia de
este archivo. CI y estado del PR se verifican por separado antes de integrar.
