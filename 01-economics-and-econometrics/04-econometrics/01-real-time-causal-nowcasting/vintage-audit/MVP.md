# Contrato de MVP

- **Qué es:** auditor ejecutable de sesgo retrospectivo por revisiones/rezagos en un nowcast OLS sintético.
- **Programa:** `04-econometrics/01-real-time-causal-nowcasting`.
- **Madurez:** componente de evaluación S1 → S2; resto del programa S1, sin reclamar S3.
- **Cómo corre:** `bash 01-economics-and-econometrics/04-econometrics/01-real-time-causal-nowcasting/vintage-audit/reproduce.sh` desde raíz.
- **Produce:** CSV crudos, JSON con seeds/hashes/hardware, figura, notebook ejecutado, tests y cobertura.
- **Baseline:** OLS exacto del núcleo del repo y media histórica; mismo target, seeds y orígenes para los brazos.
- **No cubre:** datos colombianos/reales, Kalman, MIDAS, inferencia causal, identificación estructural, equilibrio económico, modelos fundacionales ni optimización de forecasting.
- **Alcance reducido:** un indicador, dos releases, delays 0/1; auditoría de información, sin pretender resolver el programa completo.

## Checklist

- [x] Código real en src/.
- [x] Comando único de instalación y reproducción.
- [x] Tests automatizados ejecutados y aprobados.
- [x] Baseline con números en results/summary.csv.
- [x] CSV, JSON y figura generados por ejecución.
- [x] README, informe, referencias y MVP.
- [x] Carpeta del programa original, sin duplicar áreas con nombres traducidos.
- [x] Madurez declarada y limitada a S2.

La integración se realiza mediante rama y PR; no implica fusión a main.
