/*
 * use_after_free.c -- write and read through a pointer whose block was freed.
 *
 * Error class: heap-use-after-free (see CLAIMS.md, Claim 3).
 * The freed block must not be released to the allocator's free list for the
 * detection to be deterministic, so this case relies on the default
 * ASan quarantine. Do not run it with quarantine_size_mb=0.
 *
 * Build and run: scripts/run_detection.sh
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void)
{
    char *block = malloc(16);

    if (block == NULL) {
        fputs("malloc failed\n", stderr);
        return EXIT_FAILURE;
    }

    memset(block, 'A', 15);
    block[15] = '\0';
    printf("before free: %s\n", block);

    free(block);

    block[0] = 'B'; /* heap-use-after-free: write */
    printf("after free: first byte is %d\n", (int)block[0]); /* and a read */

    return EXIT_SUCCESS;
}
