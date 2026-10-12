# Integración C++

La cabecera `include/credit_risk/contracts.hpp` define únicamente tipos de dominio e invariantes compartibles con Python/SQL. No contiene motor de decisión, conectividad, datos reales ni serialización de PII.

Una implementación debe:

1. validar `RunContext::valid()` y `ExposureSnapshot::valid()` antes de estimar;
2. devolver `std::nullopt` ante entradas inválidas, sin sustituirlas silenciosamente;
3. persistir resultados solo mediante el contrato `RiskEstimate/v1` y una corrida aceptada;
4. mantener los adaptadores de base de datos y secretos fuera de esta biblioteca de dominio.

Compilación de verificación de la interfaz (sin enlazado):

```sh
c++ -std=c++17 -Wall -Wextra -Werror -fsyntax-only -xc++ -I cpp/include - <<'CPP'
#include <credit_risk/contracts.hpp>
int main() { return portfolio::credit_risk::RunContext{}.valid() ? 0 : 0; }
CPP
```
