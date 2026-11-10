# Roadmap

1. Siguiente prototipo: adaptar el paquete a un subconjunto documentado de in-toto/SLSA; verificar firma con biblioteca mantenida y expectativas externas al bundle, nunca claves auto-declaradas.
2. Pruebas de integración: export/import de un tracker ML (por ejemplo MLflow), referencias grandes/URI, rutas maliciosas, cargas truncadas, hash alternativo y compatibilidad de esquema.
3. Evaluación adversarial independiente: atacante con permisos diferenciados sobre payload, manifiesto, almacenamiento, CI y clave de firma; reporte de falsos aceptados/rechazados y latencias sobre bundles reales anonimizados o fixtures públicos licenciados.
4. Gobierno: definir roles de aprobación, políticas de revocación/expiración y retención; incluir verificación externa y anti-rollback. Si no existe root-of-trust confiable, abstenerse.
5. No ascender a validado hasta evaluación fuera de muestra, revisión de seguridad independiente y documentación de operación/rollback. Operacional requiere identidad de builder, observabilidad, control de acceso, auditoría y SLO.
