# Verificación local de integridad de evidencia ML

**Estado: prototipo M2 en simulación sintética; no validado con pipeline real ni operacional.** Implementación offline para inspeccionar paquetes declarativos de evidencia: manifiesto, artefactos, hashes, tipos requeridos y grafo de dependencias acíclico.

El verificador acepta 40/40 paquetes limpios, detecta 160/160 mutaciones ex post (payload alterado o ausente, dependencia inexistente o ciclo) y también acepta las 40 falsificaciones auto-consistentes que reescriben payload y recalculan el hash. Ese último resultado es el límite central: sin ancla externa de confianza, un hash recalculable prueba consistencia interna, no la verdad del linaje.

```bash
./run.sh
```

El comando genera `results/raw_cases.csv`, `results/summary.json` y `results/acceptance.png`, ejecuta pruebas y procesa el notebook. `config.json` fija hipótesis, escenarios y umbrales antes de leer resultados. Las fuentes y límites están en `prior_art.md`, `referencias.bib` y `MVP.md`.
