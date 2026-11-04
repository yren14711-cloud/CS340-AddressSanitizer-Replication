# Clean-machine reproduction image for the AddressSanitizer replication.
#
# The rubric asks that the main experiment can be built and run from the README
# alone on a clean machine, VM or container, with the toolchain versions pinned.
# This file is that pinned environment: everything needed to build the
# benchmarks and run the matrix, and nothing else.
#
#   docker build -t cs340-asan .
#   docker run --rm -it cs340-asan                  # build + run + parse
#   docker run --rm -it cs340-asan bash             # shell inside the image
#
# Note on base images: the measured environment is Ubuntu 26.04 (see
# results/env/environment.txt). If the ubuntu:26.04 tag is not available on your
# registry, override it, but then record the resulting clang version in the
# deviations table:
#   docker build --build-arg BASE_IMAGE=ubuntu:24.04 -t cs340-asan .

ARG BASE_IMAGE=ubuntu:26.04
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        clang \
        make \
        python3 \
        binutils \
        coreutils \
        time \
        ca-certificates \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY . /work

# Record the pinned toolchain inside the image so that a run can never be
# reported against a compiler version that nobody verified.
RUN clang --version | head -n 2 > /work/build-toolchain.txt \
    && cat /work/build-toolchain.txt

RUN make

# Default action: the "can it be reproduced from scratch" check.
CMD ["bash", "-lc", "make && scripts/collect_env.sh && scripts/run_experiments.sh && python3 scripts/parse_results.py"]
