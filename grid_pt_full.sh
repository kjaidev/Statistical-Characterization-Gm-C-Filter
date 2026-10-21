#!/bin/bash
# usage: ./grid_pt_full.sh N IREF RT ALPHA  -> all 45 conditions, sequential, skips finished ones
N=$1; IREF=$2; RT=$3; ALPHA=$4
cd /foss/designs/gmc-filter
for c in tt ss ff sf fs; do for v in 1.8 1.62 1.98; do for t in 27 -20 85; do
  tag=pt_${c}_${v}_${t}; f=results_$tag.txt
  if [ -f "$f" ] && [ "$(wc -l < $f)" -ge $((5*N)) ]; then echo "skip $tag"; continue; fi
  ./run_pt.sh $tag ${c}_mm $v $t $N $IREF $RT $ALPHA
done; done; done
echo ALLDONE
