/*
 * stack_buffer_overflow.c -- out-of-bounds write to a stack array.
 *
 * Error class: stack-buffer-overflow (see CLAIMS.md, Claim 3).
 * The write index is derived from argc so that it cannot be folded away at
 * compile time; the array is volatile so that the store is not optimised out
 * even at -O2. Run with no arguments, argc is 1 and the index is 4, one past
 * the end of a four-element array.
 *
 * Build and run: scripts/run_detection.sh
 */

#include <stdio.h>
#include <stdlib.h>

static volatile int observed;

int main(int argc, char **argv)
{
    volatile int buffer[4];
    size_t index;
    int i;

    (void)argv;

    for (i = 0; i < 4; ++i) {
        buffer[i] = i;
    }

    index = (size_t)argc + 3;
    buffer[index] = 42; /* stack-buffer-overflow */

    observed = buffer[0];
    printf("wrote buffer[%llu] (valid indices 0..3), observed=%d\n",
           (unsigned long long)index, (int)observed);
    return EXIT_SUCCESS;
}
