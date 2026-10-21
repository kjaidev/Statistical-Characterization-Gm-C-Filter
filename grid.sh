#!/bin/bash
N=${1:-1000}; P=${2:-$(nproc)}
for C in ss_mm tt_mm ff_mm sf_mm fs_mm; do for V in 1.62 1.8 1.98; do for T in -20 27 85; do
 echo "g_${C%_mm}_${V}_${T} $C $V $T $N"
done; done; done | xargs -P $P -L 1 ./run_sweep.sh
