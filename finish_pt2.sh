#!/bin/bash
# refinement: finer input common-mode points + noise spectrum (PTAT design)
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
P=".param iref=12u rt=1.48 alpha=0.6"
cd $D
mkdir -p fin_logs
mk() { sed -e "s#^.lib .*#.lib $L $1#" -e "s#^V1 VDD 0 .*#V1 VDD 0 1.8#" -e "s#^.include .*#.include $2#" -e "s#^.param .*#$P#" gmc_pt.spice > $3; sed -i "1a .temp 27" $3; }
for V in 0.6 0.65 0.75 0.8 0.85 0.95 1.0 1.2 1.25 1.35 1.4 1.45; do
  mk tt $D/cmr.cir net_cmr.spice
  sed -i -e "s#^Vinp vin 0 .*#Vinp vin 0 $V ac 1#" -e "s#^Vinn vcm 0 .*#Vinn vcm 0 $V#" net_cmr.spice
  ngspice -b net_cmr.spice > fin_logs/cmr_$V.log 2>&1; echo "done cm $V"
done
rm -f curves_noise_pt.txt
sed -e "s#@CURV@#$D/curves_noise_pt.txt#" noise.cir > noise_run.cir
mk tt $D/noise_run.cir net_noise.spice; ngspice -b net_noise.spice > fin_logs/noise.log 2>&1; echo "done noise"
echo ALLDONE
