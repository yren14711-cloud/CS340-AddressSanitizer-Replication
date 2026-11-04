/*
 * global_buffer_overflow.c -- out-of-bounds write to a global array.
 *
 * Error class: global-buffer-overflow (see CLAIMS.md, Claim 3).
 * Globals are laid out by the compiler with poisoned redzones, so the check
 * needs no allocation at all: the index comes from argc and the array is
 * volatile so that neither the layout nor the store can be optimised away.
 *
 * Build and run: scripts/run_detection.sh
 */

#include <stdio.h>
#include <stdlib.h>

static volatile int counters[4];

int main(int argc, char **argv)
{
    size_t index;
    int i;

    (void)argv;

    for (i = 0; i < 4; ++i) {
        counters[i] = i;
    }

    index = (size_t)argc + 3;
    counters[index] = 7; /* global-buffer-overflow */

    printf("wrote counters[%llu] (valid indices 0..3), counters[0]=%d\n",
           (unsigned long long)index, (int)counters[0]);
    return EXIT_SUCCESS;
}
