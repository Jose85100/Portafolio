# Derivación y condiciones

Para cada precio j, la tasa de conversión desconocida p_j tiene prior Beta(a_j,b_j). El margen m_j está expresado en unidades abstractas por cliente expuesto. El valor hoy es V0=max(0, m_A a_A/(a_A+b_A), m_B a_B/(a_B+b_B)). Cero representa cerrar.

Con n exposiciones aleatorizadas por brazo y x_j conversiones, conjugación Beta-Binomial da posterior Beta(a_j+x_j,b_j+n−x_j). La probabilidad predictiva de x es C(n,x)B(a_j+x,b_j+n−x)/B(a_j,b_j). Su masa suma uno. El valor esperado con información es la suma sobre pares (x_A,x_B) del producto de sus masas predictivas multiplicado por máximo de valores posteriores y cero.

EVSI=E[max(0,m_A E[p_A|X_A],m_B E[p_B|X_B])]-V0 ≥0: siempre se puede ignorar la muestra. Neto=EVSI−c. Pilotear si neto>0; empatar conduce a no pilotear. Posteriores de brazos independientes y asignación igual son supuestos del cálculo. La desigualdad EVSI≥0 no cubre sesgo de selección ni garantiza beneficio realizado.

Baseline justo: seleccionar hoy con el mismo menú/prior y asignar valor de opción de información cero. El piloto usa exactamente ambos precios, mismo modelo de contribución y prior; se enumera toda la distribución predictiva, sin Monte Carlo.
