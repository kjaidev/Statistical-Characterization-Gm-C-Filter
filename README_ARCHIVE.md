# Gm-C filter in SKY130, reproducibility archive

Team: Jaidev K, S Jai Akaash, Mohanakrishnan S, Jeswant P M. Faculty: Dr. Brintha Therese A.

## Tool versions
ngspice: 47 (hpretl/iic-osic-tools)
xyce: Xyce Release 7.10-opensource
ciel
gf180mcuD
ihp-sg13cmos5l
ihp-sg13g2
sky130A
versions.txt
open_pdks 026824c7969ce6f4fc9678e6ca04b0a06a596c4b

Docker image: hpretl/iic-osic-tools@sha256:3c371645b19c6f6564dc8c7b21e39ad1c1833d274fe5b85639afe1ba9d7987e7 sha256:3c371645b19c6f6564dc8c7b21e39ad1c1833d274fe5b85639afe1ba9d7987e7

## Design
Gm-C biquad, 3 OTAs, C1=C2=10 pF, PTAT current bias (Iref=12u, rt=1.48, alpha=0.6), fc 1.6 MHz, Q about 0.72.
Monte Carlo: ngspice tt_mm/ss_mm/ff_mm/sf_mm/fs_mm corners, 750 runs per condition, 45 PVT conditions.

## Run
./dk.sh "./run_pt.sh TAG CORNER_mm VDD TEMP N 12u 1.48 0.6"
streamlit run gmc_app.py
