# Desarrollo matemático — Diferencias en diferencias

> **Estado:** derivación analítica y protocolo de investigación. No se presenta como estimación empírica validada.

## 1. Problema, objetos y dominio

Definir espacio de probabilidad $(\Omega,\mathcal F,\mathbb P)$ cuando intervengan shocks aleatorios; filtrar información disponible en cada fecha con $(\mathcal F_t)$. Las decisiones deben ser medibles respecto a la información disponible antes del resultado. Separar parámetros estructurales, estados, controles, observaciones y errores de medición.

**Modelo de partida:**

$$
Y_{it}=\alpha_i+\lambda_t+\tau D_i Post_t+u_{it}
$$

Antes de calibrar, fijar unidades, índices temporales, soporte, restricciones paramétricas y la dimensión de cada variable. Verificar que las transformaciones preserven unidades y que el sistema sea identificable.

## 2. Proposición y resultado derivado

**Proposición (condicional a los supuestos indicados).** La formulación anterior implica:

$$
ATT=[E(Y_{post}-Y_{pre}|D=1)]-[E(Y_{post}-Y_{pre}|D=0)]
$$

**Derivación.** Restar diferencias temporales de tratados y controles para cancelar efectos fijos.

La proposición no establece por sí sola un efecto causal ni garantiza que los parámetros puedan estimarse consistentemente con los datos disponibles. Deben distinguirse identidades, condiciones necesarias, condiciones suficientes y aproximaciones.

## 3. Supuestos críticos y fallos del modelo

Tendencias paralelas y no anticipación; tratamientos escalonados requieren estimadores específicos.

Cuando se rompe un supuesto, analizar explícitamente: (i) si existe solución, (ii) si es única, (iii) si el estimador converge al parámetro objetivo, (iv) si la inferencia es válida, (v) si las decisiones cambian de signo. No asumir que una regresión simple recupera el parámetro estructural.

## 4. Identificación estadística y estimación

Event study, placebo, sensibilidad a tendencias y clusters.

Definir un estimando $\theta_0$ y una función objetivo $Q_n(\theta)$. Si se propone un estimador M, establecer:

$$
\widehat\theta_n\in\operatorname*{arg\,min}_{\theta\in\Theta} Q_n(\theta).
$$

Para afirmar consistencia se requieren, entre otros, identificación de minimizador único, convergencia uniforme de $Q_n$ y condiciones de compacidad/coercividad. Para normalidad asintótica, derivar expansión de primer orden y matriz sándwich cuando corresponda. No atribuir estas propiedades sin demostrar las hipótesis del modelo concreto.

## 5. Método numérico y convergencia

Simular contrafactual con efecto conocido.

Registrar función objetivo, restricciones, criterio de parada, tolerancia, semilla, complejidad y comportamiento con múltiples condiciones iniciales. Cuando haya simulación Monte Carlo con muestras independientes y varianza finita, el error estándar decrece como $O(N^{-1/2})$; esta tasa no se traslada automáticamente a procesos dependientes.

## 6. Falsación y tests obligatorios

1. **Identidad analítica:** caso límite en que el resultado pueda comprobarse exactamente.
2. **Recuperación de parámetros:** generar datos con verdad conocida y estimar sesgo, RMSE y cobertura.
3. **Restricciones:** comprobar dominios, normalización y conservación de cantidades.
4. **Estabilidad:** modificar tamaños muestrales, shocks, semillas y parámetros.
5. **Identificación:** documentar un contraejemplo donde falle el supuesto central.
6. **Validación temporal:** entrenar solo con información disponible antes de cada fecha.
7. **Benchmark:** contrastar con un modelo nulo y uno parsimonioso.

## 7. Aplicación y límites

Conectar el resultado con decisiones de fintech, crédito, pagos, tesorería o política económica según el README del proyecto. Separar hipótesis, resultados simulados y evidencia externa; registrar fuentes públicas, fecha de corte, revisiones, licencias y trazabilidad.

## 8. Relación con notebook actual

El notebook `01-estimation-and-robustness.ipynb` es un laboratorio **genérico** de OLS y bootstrap, no una implementación de la ecuación de este documento. El siguiente entregable de ingeniería debe incluir un notebook **específico** que implemente el modelo, su estimador y sus tests de propiedades.
