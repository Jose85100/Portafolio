# Antecedentes y delimitación

| Fuente | Método/alcance | Relación y diferencia de este MVP |
|---|---|---|
| Aghassi & Bertsimas (2006), DOI [10.1007/s10107-005-0686-0](https://doi.org/10.1007/s10107-005-0686-0) | Teoría de juegos robustos y pagos inciertos. | Marco general para incertidumbre estratégica; aquí se calcula un certificado de regret de un perfil fijado, no un equilibrio robusto. |
| Bertsimas & Sim (2004), DOI [10.1287/opre.1030.0065](https://doi.org/10.1287/opre.1030.0065) | Conjuntos de incertidumbre y precio de robustez en optimización. | Motiva declarar la geometría del conjunto; el factor aquí es compartido entre estados rivales con cargas propias específicas. |
| Ben-Tal & Nemirovski (1998), DOI [10.1287/moor.23.4.769](https://doi.org/10.1287/moor.23.4.769) | Optimización convexa robusta, incluidos conjuntos elipsoidales. | Antecedente metodológico; nuestro conjunto es una caja escalar de factores, resuelta por soporte analítico, sin optimización convexa numérica. |
| Nash (1950), DOI [10.1073/pnas.36.1.48](https://doi.org/10.1073/pnas.36.1.48) | Existencia de puntos de equilibrio en juegos no cooperativos finitos. | Contextualiza el objeto de equilibrio; el MVP no busca ni prueba equilibrio. |
| Harsanyi (1967), DOI [10.1287/mnsc.14.3.159](https://doi.org/10.1287/mnsc.14.3.159) | Juegos con información incompleta y tipos. | Alternativa considerada (incertidumbre de tipos), pospuesta; el factor adverso no tiene distribución ni prior. |

La búsqueda de antecedentes no fue sistemática; las referencias verifican el marco metodológico y no afirman prioridad para la fórmula elemental aquí derivada. El diferencial es pedagógico/ingenieril: una interpolación explícita entre factor común que cancela y error rectangular independiente por celda.
