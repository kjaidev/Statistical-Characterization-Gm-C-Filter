#!/bin/bash
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
TAG=pt_tight_tt_1.8_27
rm -f results_$TAG.txt
sed -e "s#ac dec 20 #ac dec 200 #" -e "s#@N@#300#" -e "s#@VDD@#1.8#" -e "s#@OUT@#$D/results_$TAG.txt#" mc_cm.cir > mcpt_$TAG.cir
sed -e "s#^.lib .*#.lib $L tt_mm#" -e "s#^V1 VDD 0 .*#V1 VDD 0 1.8#" -e "s#^.include .*#.include $D/mcpt_$TAG.cir#" -e "s#^.param .*#.param iref=12u rt=1.48 alpha=0.6#" gmc_pt.spice > netpt_$TAG.spice
sed -i "1a .temp 27\n.options reltol=1e-6 abstol=1e-14 vntol=1e-8 gmin=1e-14 itl1=500 itl4=100" netpt_$TAG.spice
ngspice -b netpt_$TAG.spice > logpt_$TAG.txt 2>&1
echo ALLDONE
