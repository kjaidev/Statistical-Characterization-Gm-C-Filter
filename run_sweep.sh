#!/bin/bash
TAG=$1; CORNER=$2; VDD=$3; TEMP=$4; N=$5
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
NET=/foss/designs/gmc-filter/gmc_top.spice
cd $D; rm -f results_$TAG.txt
sed -e "s#@TEMP@#$TEMP#" -e "s#@N@#$N#" -e "s#@VDD@#$VDD#" -e "s#@OUT@#$D/results_$TAG.txt#" mc_template.cir > mc_$TAG.cir
sed -e "s#^.lib .*#.lib $L $CORNER#" $NET > n1_$TAG.spice
sed -e "s#^V1 VDD 0 .*#V1 VDD 0 $VDD#" n1_$TAG.spice > n2_$TAG.spice
sed -e "s#^.include .*#.include $D/mc_$TAG.cir#" n2_$TAG.spice > net_$TAG.spice
sed -i "1a .temp $TEMP" net_$TAG.spice
ngspice -b net_$TAG.spice > log_$TAG.txt 2>&1
echo done $TAG
wc -l results_$TAG.txt
