/*
 * b1_malloc_text.c -- malloc churn with byte-level accesses.
 *
 * Workload class: many small heap objects touched one or two bytes at a time.
 * This is the pattern the AddressSanitizer paper (USENIX ATC 2012) attributes
 * the worst slowdowns to: 400.perlbench (2.60x) and 483.xalancbmk (2.67x) in
 * Figure 2. A fraction of the allocations is retained so that the live set,
 * and therefore the redzone-driven memory overhead, is non-trivial.
 *
 * Written for this replication; not derived from SPEC.
 *
 * Usage: ./b1_malloc_text <scale>      (scale >= 1, default 1)
 */

#include <stdio.h>
#include <stdlib.h>

typedef struct node {
    struct node *next;
    unsigned char len;
    char text[24];
} node;

#define CHURN_PER_ITER 4
#define RETAIN_EVERY   4

static void fill(node *n, long i)
{
    unsigned char t;

    n->len = (unsigned char)(1 + (i % 15));
    for (t = 0; t < n->len; ++t) {
        n->text[t] = (char)('a' + (int)((i + t) % 26));
    }
}

int main(int argc, char **argv)
{
    long scale = (argc > 1) ? strtol(argv[1], NULL, 10) : 1;
    long iters;
    long i;
    int k;
    node *retained = NULL;
    unsigned long checksum = 0;

    if (scale < 1) {
        scale = 1;
    }
    iters = 3000000L * scale;

    for (i = 0; i < iters; ++i) {
        node *n = malloc(sizeof *n);

        if (n == NULL) {
            fputs("b1: malloc failed\n", stderr);
            return EXIT_FAILURE;
        }
        fill(n, i);
        checksum += (unsigned char)n->text[n->len - 1];

        if (i % RETAIN_EVERY == 0) {
            n->next = retained;
            retained = n;
        } else {
            free(n);
        }

        /* Short-lived churn: malloc and free in the same iteration. */
        for (k = 0; k < CHURN_PER_ITER; ++k) {
            node *s = malloc(sizeof *s);

            if (s == NULL) {
                fputs("b1: malloc failed\n", stderr);
                return EXIT_FAILURE;
            }
            fill(s, i + k);
            checksum += (unsigned char)s->text[0];
            free(s);
        }
    }

    while (retained != NULL) {
        node *next = retained->next;

        checksum += (unsigned char)retained->text[retained->len - 1];
        free(retained);
        retained = next;
    }

    printf("checksum=%lu\n", checksum);
    return EXIT_SUCCESS;
}
