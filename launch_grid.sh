#!/bin/bash
docker run -d --name gmcgrid2 --user 1000:1000 \
  -e PATH=/foss/tools/bin:/usr/local/bin:/usr/bin:/bin \
  -e HOME=/headless -e OMP_NUM_THREADS=1 \
  --entrypoint bash \
  -v "$(pwd)":/foss/designs/gmc-filter \
  hpretl/iic-osic-tools \
  -c "cd /foss/designs/gmc-filter && ./grid2.sh 750 > grid2.log 2>&1"
