v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 730 -380 730 -350 {lab=0}
N 180 -640 180 -620 {lab=VDD}
N 410 -420 410 -230 {lab=vb}
N 180 -230 410 -230 {lab=vb}
N 710 -460 730 -440 {lab=vo1}
N 730 -230 730 -200 {lab=0}
C {vsource.sym} 40 -250 0 0 {name=Vinp value="0.9 ac 1" savecurrent=false}
C {vsource.sym} 180 -590 0 0 {name=V1 value=1.8 savecurrent=false}
C {gnd.sym} 180 -560 0 0 {name=l3 lab=0}
C {gnd.sym} 40 -220 0 0 {name=l4 lab=0}
C {vsource.sym} 290 -370 0 0 {name=Vinn value=0.9 savecurrent=false}
C {vsource.sym} 180 -200 0 0 {name=Vbias_tail_v value=0.7 savecurrent=false}
C {gnd.sym} 180 -170 0 0 {name=l6 lab=0}
C {code.sym} 40 -480 0 0 {name=s2 only_toplevel=false value=".lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt_mm"
}
C {code.sym} 40 -620 0 0 {name=s1 only_toplevel=false value=".include /foss/designs/gmc-filter/mc_run.cir"}
C {capa.sym} 730 -410 0 0 {name=C1
m=1
value=10p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 730 -350 0 0 {name=l8 lab=0}
C {gnd.sym} 290 -340 0 0 {name=l1 lab=0}
C {ota_core.sym} 560 -440 0 0 {name=x1}
C {vdd.sym} 180 -640 0 0 {name=l2 lab=VDD}
C {lab_pin.sym} 410 -460 0 0 {name=p2 sig_type=std_logic lab=vin}
C {lab_pin.sym} 410 -440 0 0 {name=p1 sig_type=std_logic lab=vo2}
C {lab_pin.sym} 710 -460 0 0 {name=p3 sig_type=std_logic lab=vo1}
C {lab_pin.sym} 410 -420 0 0 {name=p4 sig_type=std_logic lab=vb}
C {lab_pin.sym} 40 -280 0 0 {name=p5 sig_type=std_logic lab=vin}
C {lab_pin.sym} 290 -400 0 0 {name=p6 sig_type=std_logic lab=vcm}
C {ota_core.sym} 570 -90 0 0 {name=x2}
C {lab_pin.sym} 420 -110 0 0 {name=p7 sig_type=std_logic lab=vo1}
C {lab_pin.sym} 420 -90 0 0 {name=p8 sig_type=std_logic lab=vcm}
C {lab_pin.sym} 720 -110 0 0 {name=p9 sig_type=std_logic lab=vo2}
C {lab_pin.sym} 420 -70 0 0 {name=p10 sig_type=std_logic lab=vb}
C {ota_core.sym} 1040 -260 0 0 {name=x3}
C {lab_pin.sym} 890 -280 0 0 {name=p11 sig_type=std_logic lab=vcm}
C {lab_pin.sym} 890 -260 0 0 {name=p12 sig_type=std_logic lab=vo1}
C {lab_pin.sym} 1190 -280 0 0 {name=p13 sig_type=std_logic lab=vo1}
C {lab_pin.sym} 890 -240 0 0 {name=p14 sig_type=std_logic lab=vb3}
C {capa.sym} 730 -260 0 0 {name=C2
m=1
value=10p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 730 -200 0 0 {name=l5 lab=0}
C {lab_pin.sym} 730 -290 0 0 {name=p15 sig_type=std_logic lab=vo2}
C {vsource.sym} 860 -120 0 0 {name=Vb3 value=0.73 savecurrent=false}
C {gnd.sym} 860 -90 0 0 {name=l7 lab=0}
C {lab_pin.sym} 860 -150 0 0 {name=p16 sig_type=std_logic lab=vb3}
