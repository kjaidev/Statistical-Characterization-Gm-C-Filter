#!/bin/bash
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
sed "s#setseed 12345#setseed 54321#" mc_cm.cir > mc_cm_s2.cir
for C in "tt 1.8 27" "sf 1.62 -20"; do
  set -- $C
  CORNER=$1; VDD=$2; TEMP=$3; TAG=pt_s2_${CORNER}_${VDD}_${TEMP}
  rm -f results_$TAG.txt
  sed -e "s#@N@#1500#" -e "s#@VDD@#$VDD#" -e "s#@OUT@#$D/results_$TAG.txt#" mc_cm_s2.cir > mcpt_$TAG.cir
  sed -e "s#^.lib .*#.lib $L ${CORNER}_mm#" -e "s#^V1 VDD 0 .*#V1 VDD 0 $VDD#" -e "s#^.include .*#.include $D/mcpt_$TAG.cir#" -e "s#^.param .*#.param iref=12u rt=1.48 alpha=0.6#" gmc_pt.spice > netpt_$TAG.spice
  sed -i "1a .temp $TEMP" netpt_$TAG.spice
  ngspice -b netpt_$TAG.spice > logpt_$TAG.txt 2>&1
  echo done $TAG
done
echo ALLDONE
