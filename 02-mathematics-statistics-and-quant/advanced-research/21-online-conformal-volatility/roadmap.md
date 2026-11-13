# Ruta de madurez

1. **S2 actual:** prueba sintética iid, baseline congelado, semillas y adversidad de escala 4x.
2. **S3:** añadir procesos AR/GARCH con calibración residual condicional, cuantiles conformales adaptativos, oráculo gaussiano y cobertura por bloques; intervalos de incertidumbre entre semillas y curvas de latencia/reacción.
3. **S3:** pruebas de cambios graduales, reversión de régimen, colas t y autocorrelación; ablación de tamaño de ventana y alpha; pruebas unitarias de invariantes y análisis de sensibilidad pre-registrado.
4. **S4:** replicación en series públicas licenciadas con partición cronológica, protocolo ciego y comparación con métodos adaptativos publicados; evaluación de fallos, dependencia y calibración condicional.
5. **Producto:** solo considerar uso en monitoreo exploratorio tras validación externa y gobierno del modelo. No apto para uso de límites o capital actualmente.
