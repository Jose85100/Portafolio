# Transporte de resúmenes: qué se conserva y qué se pierde

## Original y brecha
El programa conserva Welford desplazado29, escala externa30, autoescala31 y fusión Chan entre escalas1nov. El resumen es (n,e,a,b,Q,i): n conteo, e exponente entero, a origen, b media relativa, Q suma centrada normalizada, i indica si hubo algún dato no nulo. Para y=x/2^e, μ_y=a+b y Q=Σ(y−μ_y)². Datos x tienen unidades U; y,a,b,Q son adimensionales. μ_x=2^e(a+b), V_d=2^{2e}Q/(n−d), SD_d=2^e sqrt(Q/(n−d)), d∈{0,1}, n>d. No hay un nuevo estimador.

La limitación del1nov era una API sólo en memoria Python. Hoy exportamos suficientes estadísticas numéricas a un consumidor C++20 real. No traducimos notebooks ni eliminamos fórmulas; el notebook enseña el contrato y llama al ejecutable.

## Identidad de serialización
Un binary64 finito representable es x=s·M·2^k con s∈{−1,1}, M entero de hasta53bits y k entero. `float.hex()` escribe esos bits como mantisa hexadecimal y exponente binario; cuatro bits por dígito hexadecimal evitan redondeo decimal de transporte. `float.fromhex` y `strtod` sobre la salida de exportación reconstruyen el mismo double bajo el toolchain probado. Se exige binary64 y redondeo habitual; no se demuestra equivalencia para toda implementación de C++.

El protocolo local es una línea ASCII con siete campos: `MOMENTS_V1 n e a_hex b_hex Q_hex initialized`. Exporta estado numérico, no contador histórico de reescalados o pérdidas. Al importar, esos diagnósticos se reinician a0; esto es explícito y evita confundir un resumen transportado con su trazabilidad completa. Datos originales, identidad de filas, autenticidad, firma y procedencia no están codificados.

## Derivación de la operación consumida
Para resúmenes disjuntos A,B, E es el mayor exponente entre resúmenes no nulos; un chunk de ceros no fija unidad. c_j=2^{e_j−E}; y'_j=c_jy_j. La media es lineal: a'_j=c_ja_j, b'_j=c_jb_j. Las diferencias centradas escalan por c_j, por lo que Q'_j=c_j²Q_j. Entonces:
$$a'_j=2^{e_j-E}a_j,\quad b'_j=2^{e_j-E}b_j,\quad Q'_j=2^{2(e_j-E)}Q_j.$$
$$\delta=(a'_B-a'_A)+(b'_B-b'_A),\quad n=n_A+n_B,$$
$$a=a'_A,\quad b=b'_A+\delta\frac{n_B}{n},\quad Q=Q'_A+Q'_B+\delta^2\frac{n_A n_B}{n}.$$
La última identidad sigue de separar Σ_A(y−μ)²=Q_A+n_A(μ_A−μ)² y B análogo: los términos cruzados son0 porque las desviaciones respecto de la media de cada grupo suman0. Sustituyendo μ_A−μ=−δn_B/n y μ_B−μ=δn_A/n se obtiene el término adicional. Es Chan conocido, no una fórmula científica nueva. `moments.hpp::merge` reproduce la operación después de parsear snapshots; `result_json` devuelve SD/varianza con los mismos estados de abstención que Python.

## Dominio y límites
Conteo 0≤n≤2^53−1; la suma de conteos no debe exceder ese máximo. Exponente −1073..1024, componentes finitos, |a|≤1, |b|≤2, 0≤Q≤4n. Estado vacío o sin dato no nulo exige exponent0 y componentes0. Son validaciones estructurales conservadoras, no prueba de que un estado provino de observaciones reales. El consumidor asume snapshots de productores válidos y particiones disjuntas; no identifica solapamiento ni valida causalidad/independencia.

En reales se conservan conteo, media y suma centrada. En máquina, serialización exacta no vuelve exacta la aritmética posterior ni recupera bits ya perdidos. Reescalar órdenes extremos puede redondear componentes a0; la pérdida histórica no viaja en este V1. Sólo se transportan estadísticas: no se pueden reconstruir observaciones ni recalcular otro estimando. Casos std_underflow/std_overflow devuelven SDnull; variance_underflow/overflow pueden conservar SD. El test[-minsubnormal,minsubnormal] conserva SDmin; [0,minsubnormal] puede abstenerse porque SDrealmin/2 no cabe. Exportar primero un decimal truncado es una ablación conceptualmente distinta y no se usa para fabricar superioridad.

## Utilidad y coste
Dos resúmenes ocupan un número constante de campos frente a n floats originales; bytes exactos y coste se miden. El proceso C++ se lanza por llamada: el coste de IPC domina, y no hay promesa de aceleración. El valor es conectar resúmenes y evitar reenvío de filas, no ganar a NumPy ni aportar un nuevo resultado estadístico. Ninguna garantía de privacidad diferencial: estadísticas también pueden revelar información.
