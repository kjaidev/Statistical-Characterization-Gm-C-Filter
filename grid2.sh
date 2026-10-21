#!/bin/bash
# usage: ./grid2.sh N   (sequential, skips conditions whose results file already has >= 5*N lines)
N=${1:-200}
cd /foss/designs/gmc-filter
for c in tt ss ff sf fs; do
 for v in 1.8 1.62 1.98; do
  for t in 27 -20 85; do
   tag=g_${c}_${v}_${t}
   f=results_$tag.txt
   if [ -f "$f" ] && [ "$(wc -l < $f)" -ge $((5*N)) ]; then echo "skip $tag"; continue; fi
   ./run_sweep.sh $tag ${c}_mm $v $t $N
   echo "done $tag"
  done
 done
done
echo ALLDONE
