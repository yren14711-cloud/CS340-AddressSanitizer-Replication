/*
 * b3_matmul.c -- dense floating-point matrix multiplication.
 *
 * Workload class: arithmetic-heavy, bandwidth-bound, almost no heap activity.
 * It is the low end of the overhead range: AddressSanitizer instruments the
 * three array accesses per inner iteration, but there are only a handful of
 * allocations, so the redzone cost is negligible. The paper's 410.bwaves and
 * 433.milc play this role in Figure 2.
 *
 * Written for this replication; not derived from SPEC.
 *
 * Usage: ./b3_matmul <scale>           (scale >= 1, default 1; n = 400 * scale)
 */

#include <stdio.h>
#include <stdlib.h>

#define BASE_N 720

static double *alloc_matrix(size_t n)
{
    double *m = malloc(n * n * sizeof *m);

    if (m == NULL) {
        fputs("b3: malloc failed\n", stderr);
        exit(EXIT_FAILURE);
    }
    return m;
}

int main(int argc, char **argv)
{
    long scale = (argc > 1) ? strtol(argv[1], NULL, 10) : 1;
    size_t n;
    size_t i;
    size_t j;
    size_t k;
    double *a;
    double *b;
    double *c;
    double checksum = 0.0;

    if (scale < 1) {
        scale = 1;
    }
    if (scale > 4) {
        scale = 8; /* n = 2880 already needs ~200 MB */
    }
    n = (size_t)BASE_N * (size_t)scale;

    a = alloc_matrix(n);
    b = alloc_matrix(n);
    c = alloc_matrix(n);

    for (i = 0; i < n; ++i) {
        for (j = 0; j < n; ++j) {
            a[i * n + j] = (double)((i * 31 + j * 17) % 23) / 23.0;
            b[i * n + j] = (double)((i * 13 + j * 7) % 19) / 19.0;
            c[i * n + j] = 0.0;
        }
    }

    for (i = 0; i < n; ++i) {
        for (k = 0; k < n; ++k) {
            const double aik = a[i * n + k];

            for (j = 0; j < n; ++j) {
                c[i * n + j] += aik * b[k * n + j];
            }
        }
    }

    for (i = 0; i < n; ++i) {
        checksum += c[i * n + (i % n)];
    }

    printf("n=%llu checksum=%.6f\n", (unsigned long long)n, checksum);
    free(a);
    free(b);
    free(c);
    return EXIT_SUCCESS;
}
