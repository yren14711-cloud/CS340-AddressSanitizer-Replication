
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    const size_t count = 5;

    int *numbers = malloc(count * sizeof(*numbers));

    if (numbers == NULL) {
        perror("malloc");
        return EXIT_FAILURE;
    }

    for (size_t i = 0; i < count; ++i) {
        numbers[i] = (int)(i + 1);
    }

    printf("Allocated %zu integers; valid indices are 0 through %zu.\n",
           count, count - 1);
    printf("Intentionally reading numbers[%zu] to test AddressSanitizer.\n",
           count);
    fflush(stdout);

    volatile size_t invalid_index = count;

    // Intentional heap-buffer-overflow for ASan testing.
    int value = numbers[invalid_index];

    printf("Unexpected value: %d\n", value);

    free(numbers);
    return EXIT_SUCCESS;
}
