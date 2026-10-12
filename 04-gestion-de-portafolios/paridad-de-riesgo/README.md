# Portafolio de paridad de riesgo

Portafolio de paridad de riesgo (equal risk contribution) resuelto numéricamente. Compara pesos y contribuciones al riesgo frente a un portafolio de pesos iguales y frente a uno de mínima varianza.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas scipy
python3 main.py
```

## Resultado de ejemplo

```text
pesos_iguales: volatilidad 8.422%
  pesos: {'acciones': 0.2, 'bonos_largos': 0.2, 'bonos_corp': 0.2, 'oro': 0.2, 'inmobiliario': 0.2}
  % del riesgo: {'acciones': 0.313, 'bonos_largos': 0.055, 'bonos_corp': 0.154, 'oro': 0.164, 'inmobiliario': 0.314}
min_varianza: volatilidad 6.356%
  pesos: {'acciones': 0.179, 'bonos_largos': 0.687, 'bonos_corp': 0.0, 'oro': 0.134, 'inmobiliario': 0.0}
  % del riesgo: {'acciones': 0.177, 'bonos_largos': 0.688, 'bonos_corp': 0.0, 'oro': 0.135, 'inmobiliario': 0.0}
paridad_riesgo: volatilidad 7.196%
  pesos: {'acciones': 0.14, 'bonos_largos': 0.347, 'bonos_corp': 0.195, 'oro': 0.189, 'inmobiliario': 0.129}
  % del riesgo: {'acciones': 0.2, 'bonos_largos': 0.2, 'bonos_corp': 0.2, 'oro': 0.2, 'inmobiliario': 0.2}
```
