# Contratos de datos y ELT incremental: correcto bajo duplicados, desorden, caídas y esquemas cambiantes

Contratos de datos con cuarentena, compatibilidad de esquemas verificada por fuerza bruta, un pipeline medallón sobre SQLite (transaccional, idempotente por lote, independiente del orden), dimensiones tipo 2 y conciliación con huella de contenido. Cada propiedad se mide contra una verdad conocida y se compara con el diseño ingenuo.

## Hallazgos (medidos en el notebook)

- Los contratos detectan el 100 % de los defectos locales (sin falsos positivos) y 0 % de un cambio de unidad ×100; un monitor estadístico por lote lo detecta en 5 de 5 lotes.
- La tabla de compatibilidad de esquemas coincide con la fuerza bruta en los 12 cambios típicos y tiene 0 violaciones de solidez en 459 pares aleatorios.
- Entrega caótica: «anexar» deja +27,5 % de error en el total; «último que llega gana» deja 218 pedidos con monto desactualizado (93 % de las celdas del oro mal) si los lotes llegan barajados; el pipeline queda con error cero.
- **Error real encontrado por la prueba de caos:** validar la llave primaria por lote mandaba correcciones legítimas a cuarentena (31 filas, 8 montos viejos). Se corrigió y se fijó con una prueba unitaria.
- Con ~25 caídas inyectadas por corrida, el estado final es idéntico al sin caídas en 60/60; anexar sin transacción duplica filas en el 100 % de las corridas.
- El oro incremental escanea ~10 % de las filas el día 40 y coincide con la reconstrucción completa.
- Cerrar el día a la medianoche pierde el 2,0 % de los eventos por llegadas tardías; con tolerancia de 1 h, 0,49 %.
- Unir con el estado actual de una dimensión atribuye mal el 21,9 % del ingreso (el plan «team» queda +74 %); el tipo 2 lo evita.
- La huella de contenido detecta el 100 % de las corrupciones reales; el conteo y la suma no ven el intercambio de montos ni +x/−x.

## Estructura

```text
src/        librería (`contracts`, `evolution`, `pipeline`, `scd2`, `reconcile`)
tests/      pruebas unitarias (unittest)
docs/       ARCHITECTURE.md (diagrama y decisiones de diseño)
notebook.ipynb   desarrollo completo con pruebas automáticas (assert) y lecturas calculadas desde los datos
main.py     demostración corta
```

## Cómo ejecutar

```bash
python3 main.py                              # demostración corta
python3 -m unittest discover -s tests        # pruebas unitarias
python3 -m unittest tests.test_notebooks     # (desde la raíz del repo) ejecuta los notebooks
```

## Datos

Simulación con semilla fija y verdad conocida; sin datos reales ni confidenciales.

## Límites

- SQLite no escala a producción; el diseño ilustra las propiedades, no un lakehouse.
- Un solo escritor a la vez (sin concurrencia).
- El monitor estadístico se probó con un solo defecto semántico (cambio de escala).
