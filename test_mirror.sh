#!/bin/bash
cd /foss/designs/gmc-filter
for M in 1 4 16; do
  for T in 27 -20; do
    ./run_ptm.sh ptm_m${M}_tt_1.8_${T} tt_mm 1.8 $T 750 12u 1.48 0.6 $M
  done
done
echo ALLDONE
