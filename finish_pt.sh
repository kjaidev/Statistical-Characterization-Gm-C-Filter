#!/bin/bash
# final-design checks (PTAT current-mode bias): iref=12u rt=1.48 alpha=0.6
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
P=".param iref=12u rt=1.48 alpha=0.6"
cd $D
mkdir -p fin_logs
mk() { # corner cirfile out  (nominal-style netlist, 27C, VDD 1.8)
  sed -e "s#^.lib .*#.lib $L $1#" -e "s#^V1 VDD 0 .*#V1 VDD 0 1.8#" -e "s#^.include .*#.include $2#" -e "s#^.param .*#$P#" gmc_pt.spice > $3
  sed -i "1a .temp 27" $3
}
# 1) nominal AC curves
sed -e "s#@CURV@#$D/curves_nom_pt.txt#" nomac.cir > nomac_run.cir; rm -f curves_nom_pt.txt
mk tt $D/nomac_run.cir net_nomac.spice; ngspice -b net_nomac.spice > fin_logs/nomac.log 2>&1; echo "done nominal AC"
# 2) offset Monte Carlo (750 runs)
rm -f results_off_pt.txt
sed -e "s#@N@#750#" -e "s#@OUT@#$D/results_off_pt.txt#" mc_off.cir > mc_off_run.cir
mk tt_mm $D/mc_off_run.cir net_off.spice; ngspice -b net_off.spice > fin_logs/off.log 2>&1; echo "done offset MC"
# 3) input common-mode sweep
for V in 0.3 0.5 0.7 0.9 1.1 1.3 1.5; do
  mk tt $D/cmr.cir net_cmr.spice
  sed -i -e "s#^Vinp vin 0 .*#Vinp vin 0 $V ac 1#" -e "s#^Vinn vcm 0 .*#Vinn vcm 0 $V#" net_cmr.spice
  ngspice -b net_cmr.spice > fin_logs/cmr_$V.log 2>&1; echo "done cm $V"
done
# 4) noise
mk tt $D/noise.cir net_noise.spice; ngspice -b net_noise.spice > fin_logs/noise.log 2>&1; echo "done noise"
echo ALLDONE
