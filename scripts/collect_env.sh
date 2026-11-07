#!/bin/bash
echo "CS340 AddressSanitizer Replication"
echo "Experiment: Environment Information Collection"
echo "Date (UTC): $(date -u)"
echo "Environment: Ubuntu on Windows WSL2"
echo ""
echo "=== Operating System ==="
cat /etc/os-release | grep PRETTY_NAME
echo ""
echo "=== Linux Kernel ==="
uname -r
echo ""
echo "=== Architecture ==="
uname -m
echo ""
echo "=== Compiler Version ==="
clang --version 2>/dev/null || gcc --version
echo ""
echo "=== Git Version ==="
git --version
echo ""
echo "=== Starting Git Commit ==="
git rev-parse HEAD