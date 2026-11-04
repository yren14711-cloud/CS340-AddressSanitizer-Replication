/*
 * b4_string_scan.c -- byte-wise parsing of a large text buffer.
 *
 * Workload class: a single large input scanned byte by byte, with a separate
 * output array that grows through repeated realloc. It stands in for the text
 * and XML processing workloads (483.xalancbmk, 400.perlbench) that the paper
 * reports as the worst cases, and it exercises the checks that dominate
 * AddressSanitizer's time overhead: one shadow lookup per byte load.
 *
 * Written for this replication; not derived from SPEC.
 *
 * Usage: ./b4_string_scan <scale>      (scale >= 1, default 1)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define BASE_BYTES  (48u << 20)
#define PASSES      4

static void build_text(char *text, size_t len)
{
    uint64_t state = 0x2545F4914F6CDD1Dull;
    size_t i = 0;
    unsigned word_len = 0;

    while (i < len) {
        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;

        if (word_len == 0) {
            word_len = 1 + (unsigned)(state % 12);
            if (i < len) {
                text[i++] = (char)('a' + (int)(state % 26));
                --word_len;
            }
        } else if (i < len) {
            text[i++] = (char)('a' + (int)((state >> 8) % 26));
            --word_len;
        }

        if (word_len == 0 && i < len) {
            uint64_t pick = state >> 16;

            text[i++] = ((pick % 7) == 0) ? '\n' : (((pick % 5) == 0) ? ',' : ' ');
        }
    }
}

int main(int argc, char **argv)
{
    long scale = (argc > 1) ? strtol(argv[1], NULL, 10) : 1;
    size_t len;
    char *text;
    size_t *offsets = NULL;
    size_t cap = 1024;
    size_t ntok = 0;
    unsigned long checksum = 0;
    int pass;

    if (scale < 1) {
        scale = 1;
    }
    if (scale > 8) {
        scale = 8;
    }
    len = (size_t)BASE_BYTES * (size_t)scale;

    text = malloc(len);
    if (text == NULL) {
        fputs("b4: malloc failed\n", stderr);
        return EXIT_FAILURE;
    }
    build_text(text, len);

    offsets = malloc(cap * sizeof *offsets);
    if (offsets == NULL) {
        fputs("b4: malloc failed\n", stderr);
        return EXIT_FAILURE;
    }

    for (pass = 0; pass < PASSES; ++pass) {
        ntok = 0;
        for (size_t i = 0; i < len; ++i) {
            const unsigned char c = (unsigned char)text[i];
            const int is_sep = (c == ' ' || c == '\n' || c == ',');

            checksum += c;
            if (!is_sep) {
                continue;
            }
            if (i > 0 && (unsigned char)text[i - 1] != ' ' &&
                (unsigned char)text[i - 1] != '\n') {
                if (ntok == cap) {
                    size_t *grown;

                    cap *= 2;
                    grown = realloc(offsets, cap * sizeof *offsets);
                    if (grown == NULL) {
                        fputs("b4: realloc failed\n", stderr);
                        free(offsets);
                        free(text);
                        return EXIT_FAILURE;
                    }
                    offsets = grown;
                }
                offsets[ntok++] = i;
            }
        }
    }

    for (size_t i = 0; i < ntok; ++i) {
        checksum += (unsigned long)offsets[i];
    }

    printf("bytes=%llu tokens=%llu checksum=%lu\n",
           (unsigned long long)len, (unsigned long long)ntok, checksum);
    free(offsets);
    free(text);
    return EXIT_SUCCESS;
}
