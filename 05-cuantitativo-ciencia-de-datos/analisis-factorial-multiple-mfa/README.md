# Análisis factorial múltiple (MFA) con datos reales

Notebook extenso de MFA sobre 26 indicadores del Banco Mundial (licencia CC BY 4.0) agrupados en 5 temas (economía, salud, educación y digital, sociedad, ambiente y energía) para 171 países.

Incluye: motor MFA propio validado con identidades y un mundo sintético, ACP por grupo, Lg y RV con permutación, número de ejes (Horn, bastón roto, condicional y estabilidad por bootstrap), círculos de correlación, planos, puntos parciales, variables suplementarias con elipses bootstrap, clusters estilo HCPC (silhouette, gap, Jaccard), países de frontera y una sección de robustez (transformaciones, imputación, umbral, ACP vs MFA, quitar un grupo, quitar un país).

## Datos

Reales y abiertos: `datos/` contiene los CSV descargados con `descargar_datos.py` (último valor disponible 2015-2022). Sin datos confidenciales.

## Cómo ejecutar

```bash
jupyter nbconvert --to notebook --execute notebook.ipynb
```
