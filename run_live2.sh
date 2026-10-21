#!/bin/bash
# usage: run_live2.sh TAG CORNER VDD TEMP N SEED DESIGN   (DESIGN: v | pt | pt4)
TAG=$1; CORNER=$2; VDD=$3; TEMP=$4; N=$5; SEED=${6:-12345}; DES=${7:-v}
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
case $DES in
  pt)  NET=gmc_pt.spice;   PAR=".param iref=12u rt=1.48 alpha=0.6" ;;
  pt4) NET=gmc_pt_m.spice; PAR=".param iref=12u rt=1.48 alpha=0.6 mref=4" ;;
  *)   NET=gmc_top.spice;  PAR="" ;;
esac
rm -f results_$TAG.txt curves_$TAG.txt
sed -e "s#@N@#$N#" -e "s#@VDD@#$VDD#" -e "s#@SEED@#$SEED#" -e "s#@OUT@#$D/results_$TAG.txt#" -e "s#@CURV@#$D/curves_$TAG.txt#" mc_live.cir > mclive_$TAG.cir
sed -e "s#^.lib .*#.lib $L $CORNER#" -e "s#^V1 VDD 0 .*#V1 VDD 0 $VDD#" -e "s#^.include .*#.include $D/mclive_$TAG.cir#" $NET > netlive_$TAG.spice
[ -n "$PAR" ] && sed -i "s#^.param .*#$PAR#" netlive_$TAG.spice
sed -i "1a .temp $TEMP" netlive_$TAG.spice
ngspice -b netlive_$TAG.spice > loglive_$TAG.txt 2>&1
echo done $TAG
