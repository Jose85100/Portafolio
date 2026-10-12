/* Pérdida esperada ilustrativa en C11: structs y validación explícita. */
#include <math.h>
#include <stddef.h>
#include <stdio.h>

typedef struct {
    double pd, lgd, ead;
} Exposure;

int expected_loss(const Exposure *items, size_t n, double *result) {
    if (result == NULL || (n > 0 && items == NULL)) return -1;
    double total = 0.0, compensation = 0.0;
    for (size_t i = 0; i < n; ++i) {
        const Exposure x = items[i];
        if (!isfinite(x.pd) || !isfinite(x.lgd) || !isfinite(x.ead) ||
            x.pd < 0.0 || x.pd > 1.0 || x.lgd < 0.0 || x.lgd > 1.0 ||
            x.ead < 0.0) return -2;
        double term = x.pd * x.lgd * x.ead;
        if (!isfinite(term)) return -3;
        /* Suma compensada de Neumaier simplificada (Kahan). */
        double y = term - compensation;
        double t = total + y;
        compensation = (t - total) - y;
        total = t;
    }
    *result = total;
    return 0;
}

int main(void) {
    const Exposure exposures[] = {
        {0.02, 0.4, 1000}, {0.05, 0.6, 2000}, {0.10, 0.3, 500}
    };
    double value = 0.0;
    if (expected_loss(exposures, 3, &value) != 0) return 1;
    if (fabs(value - 83.0) > 1e-10) return 2;
    printf("EL=%.10f\n", value);
    return 0;
}
