#!/bin/bash
D=/foss/designs/gmc-filter
cd $D
sed -E '/^\.lib /s/ tt$/ tt_mm/' xy_ac.cir > xy_mm.cir
grep -m1 '^\.lib' xy_mm.cir
for s in 1 2 3 4 5; do
 rm -f xy_mm.cir.FD.prn
 Xyce -randseed $s xy_mm.cir > xy_mm_$s.log 2>&1
 echo -n "seed $s: "; python3 xyc.py xy_mm.cir.FD.prn 2>&1 | tail -1
 grep -i -m2 "error\|fatal" xy_mm_$s.log
done
