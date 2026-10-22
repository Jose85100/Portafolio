# Collateral Liquidity Choice

MVP reproducible de una decisión bancaria acotada entre liquidar un activo y cubrir el faltante con préstamo colateralizado. Extiende el bloque S2 de ventas forzadas; no implementa el modelo completo de Bichuch–Feinstein ni un equilibrio de red.

## Un comando

Desde la raíz, con Python 3.12, Linux y acceso inicial a PyPI:

```bash
bash 01-economics-and-econometrics/05-macrofinance/01-sovereign-bank-strategic-nexus/collateral-liquidity-choice/reproduce.sh
```

Instala dependencias fijadas, ejecuta Ruff, mypy estricto, cobertura, tests propios, núcleo común y regresiones financieras; genera CSV, JSON, figura y notebook ejecutado.

## Hipótesis falsable

Con faltante 0,4, activo 1, impacto 0,5, piso 0,1, fracción pignorable 0,3 y tasa 0,1, la combinación factible debe reducir liquidación y costo privado al menos 50% frente a liquidación pura. El solver debe quedar a ≤1e-5 del baseline de 200.001 puntos.

## Madurez

- Componente de elección de liquidez: **S2**.
- `Sovereign–Bank Strategic Nexus`: **S2 parcial**; juego dinámico e identificación siguen S1.
- No asciende a S3: faltan red, identificación, robustez externa y validación independiente.

Véanse `MVP.md`, `informe.md`, `referencias.bib` y `results/`.
