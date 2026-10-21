#!/bin/bash
# usage: run_ptm.sh TAG CORNER VDD TEMP N IREF RT ALPHA MREF
TAG=$1; CORNER=$2; VDD=$3; TEMP=$4; N=$5; IREF=$6; RT=$7; ALPHA=$8; MREF=$9
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
rm -f results_$TAG.txt
sed -e "s#@N@#$N#" -e "s#@VDD@#$VDD#" -e "s#@OUT@#$D/results_$TAG.txt#" mc_cm.cir > mcptm_$TAG.cir
G=gen_$TAG.txt; : > $G
for i in $(seq 1 $MREF); do
  echo "XMr_$i vbn vbn 0 0 sky130_fd_pr__nfet_01v8 L=1 W=6 nf=1 ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0" >> $G
  echo "XMr3_$i vbn3 vbn3 0 0 sky130_fd_pr__nfet_01v8 L=1 W=6 nf=1 ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0" >> $G
done
grep -v '^XMr' gmc_pt_m.spice | sed -e "s#^.lib .*#.lib $L $CORNER#" -e "s#^V1 VDD 0 .*#V1 VDD 0 $VDD#" -e "s#^.include .*#.include $D/mcptm_$TAG.cir#" -e "s#^.param .*#.param iref=$IREF rt=$RT alpha=$ALPHA mref=$MREF#" > netptm_$TAG.spice
sed -i "1r $G" netptm_$TAG.spice
sed -i "1a .temp $TEMP" netptm_$TAG.spice
ngspice -b netptm_$TAG.spice > logptm_$TAG.txt 2>&1
echo done $TAG
