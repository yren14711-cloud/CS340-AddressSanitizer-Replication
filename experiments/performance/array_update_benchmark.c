#define _POSIX_C_SOURCE 200809L

#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define ELEMENTS (16u * 1024u * 1024u)
#define PASSES 200u

int main(void) {
    size_t count = (size_t)ELEMENTS;

    uint32_t *data = malloc(count * sizeof(*data));

    if (data == NULL) {
        perror("malloc");
        return EXIT_FAILURE;
    }

    /* Initialize the array before timing */
    for (size_t i = 0; i < count; i++) {
        data[i] = (uint32_t)i;
    }

    struct timespec start, end;

    if (clock_gettime(CLOCK_MONOTONIC, &start) != 0) {
        perror("clock_gettime");
        free(data);
        return EXIT_FAILURE;
    }

    /* Main benchmark workload */
    for (size_t pass = 0; pass < PASSES; pass++) {
        for (size_t i = 0; i < count; i++) {
            data[i] = data[i] * UINT32_C(1664525)
                      + UINT32_C(1013904223);
        }
    }

    if (clock_gettime(CLOCK_MONOTONIC, &end) != 0) {
        perror("clock_gettime");
        free(data);
        return EXIT_FAILURE;
    }

    double elapsed =
        (end.tv_sec - start.tv_sec) +
        (end.tv_nsec - start.tv_nsec) / 1000000000.0;

    /* Calculate checksum to verify the final data */
    uint64_t checksum = 0;

    for (size_t i = 0; i < count; i++) {
        checksum += data[i];
    }

    printf("workload=array_update\n");
    printf("elements=%zu\n", count);
    printf("passes=%u\n", PASSES);
    printf("array_size_bytes=%zu\n",
           count * sizeof(*data));
    printf("elapsed_seconds=%.9f\n", elapsed);
    printf("checksum=%" PRIu64 "\n", checksum);

    free(data);

    return EXIT_SUCCESS;
}
