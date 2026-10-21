#!/bin/bash
# usage: ./dk.sh "command"            run in the tool container (foreground)
#        ./dk.sh -d NAME "command"    run detached as container NAME
cd "$(dirname "$0")"
OPTS="--user 1000:1000 -e PATH=/foss/tools/bin:/usr/local/bin:/usr/bin:/bin -e HOME=/headless -e OMP_NUM_THREADS=1 --entrypoint bash -v $(pwd):/foss/designs/gmc-filter"
if [ "$1" = "-d" ]; then
  docker rm -f "$2" >/dev/null 2>&1
  docker run -d --name "$2" $OPTS hpretl/iic-osic-tools -c "cd /foss/designs/gmc-filter && $3"
else
  docker run --rm $OPTS hpretl/iic-osic-tools -c "cd /foss/designs/gmc-filter && $1"
fi
