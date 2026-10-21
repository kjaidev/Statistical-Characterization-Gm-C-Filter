#!/bin/bash
# usage: ./grid_pt.sh N IREF RT ALPHA   (sequential, skips finished conditions)
N=$1; IREF=$2; RT=$3; ALPHA=$4
cd /foss/designs/gmc-filter
run() {
  tag=pt_$1_$2_$3; f=results_$tag.txt
  if [ -f "$f" ] && [ "$(wc -l < $f)" -ge $((5*N)) ]; then echo "skip $tag"; return; fi
  ./run_pt.sh $tag $1_mm $2 $3 $N $IREF $RT $ALPHA
}
for c in tt ss ff sf fs; do for t in 27 -20 85; do run $c 1.8 $t; done; done
run tt 1.62 27
run tt 1.98 27
echo ALLDONE
