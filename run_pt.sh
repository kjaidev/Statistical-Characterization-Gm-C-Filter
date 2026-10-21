#!/bin/bash
# usage: run_pt.sh TAG CORNER VDD TEMP N IREF RT ALPHA
TAG=$1; CORNER=$2; VDD=$3; TEMP=$4; N=$5; IREF=$6; RT=$7; ALPHA=$8
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
rm -f results_$TAG.txt
sed -e "s#@N@#$N#" -e "s#@VDD@#$VDD#" -e "s#@OUT@#$D/results_$TAG.txt#" mc_cm.cir > mcpt_$TAG.cir
sed -e "s#^.lib .*#.lib $L $CORNER#" -e "s#^V1 VDD 0 .*#V1 VDD 0 $VDD#" -e "s#^.include .*#.include $D/mcpt_$TAG.cir#" -e "s#^.param .*#.param iref=$IREF rt=$RT alpha=$ALPHA#" gmc_pt.spice > netpt_$TAG.spice
sed -i "1a .temp $TEMP" netpt_$TAG.spice
ngspice -b netpt_$TAG.spice > logpt_$TAG.txt 2>&1
echo done $TAG
