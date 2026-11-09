/*
 * b2_pointer_chase.c -- dependent random loads over a permuted index array.
 *
 * Workload class: latency-bound pointer chasing with cache misses and one large
 * allocation. AddressSanitizer instruments every one of the loads, so the time
 * cost is high, while the memory cost is near zero because a 32-byte redzone
 * around a multi-megabyte block is negligible. That contrast is the reason this
 * benchmark is in the set: it shows that the paper's 3.37x average memory
 * figure is driven by small allocations, not by allocation count alone.
 *
 * Written for this replication; not derived from SPEC.
 *
 * Usage: ./b2_pointer_chase <scale>    (scale >= 1, default 1)
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define BASE_NODES  (4u << 20)
#define BASE_STEPS  12000000L

int main(int argc, char **argv)
{
    long scale = (argc > 1) ? strtol(argv[1], NULL, 10) : 1;
    uint32_t nodes;
    uint32_t *perm;
    uint64_t state = 88172645463325252ull;
    long steps;
    long k;
    uint32_t idx = 0;
    unsigned long checksum = 0;

    if (scale < 1) {
        scale = 1;
    }
    if (scale > 16) {
        scale = 16; /* keep the index array sane */
    }
    nodes = BASE_NODES * (uint32_t)scale;
    steps = BASE_STEPS * scale;

    perm = malloc((size_t)nodes * sizeof *perm);
    if (perm == NULL) {
        fputs("b2: malloc failed\n", stderr);
        return EXIT_FAILURE;
    }

    for (uint32_t i = 0; i < nodes; ++i) {
        perm[i] = i;
    }

    /* Deterministic Fisher-Yates shuffle (xorshift64). */
    for (uint32_t i = nodes - 1; i > 0; --i) {
        uint32_t j;
        uint32_t tmp;

        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;
        j = (uint32_t)(state % (uint64_t)(i + 1));
        tmp = perm[i];
        perm[i] = perm[j];
        perm[j] = tmp;
    }

    for (k = 0; k < steps; ++k) {
        idx = perm[idx];
        checksum += idx;
    }

    printf("checksum=%lu\n", checksum);
    free(perm);
    return EXIT_SUCCESS;
}
