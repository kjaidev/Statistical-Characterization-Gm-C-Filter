#!/bin/bash
TAG=$1; CORNER=$2; VDD=$3; TEMP=$4; N=$5; SEED=${6:-12345}
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
rm -f results_$TAG.txt curves_$TAG.txt
sed -e "s#@N@#$N#" -e "s#@VDD@#$VDD#" -e "s#@SEED@#$SEED#" -e "s#@OUT@#$D/results_$TAG.txt#" -e "s#@CURV@#$D/curves_$TAG.txt#" mc_live.cir > mclive_$TAG.cir
sed -e "s#^.lib .*#.lib $L $CORNER#" -e "s#^V1 VDD 0 .*#V1 VDD 0 $VDD#" -e "s#^.include .*#.include $D/mclive_$TAG.cir#" gmc_top.spice > netlive_$TAG.spice
sed -i "1a .temp $TEMP" netlive_$TAG.spice
ngspice -b netlive_$TAG.spice > loglive_$TAG.txt 2>&1
echo done $TAG
