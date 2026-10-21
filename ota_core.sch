v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 300 -290 480 -290 {lab=#net1}
N 390 -290 390 -260 {lab=#net1}
N 260 -410 300 -410 {lab=#net2}
N 260 -440 260 -410 {lab=#net2}
N 260 -520 260 -440 {lab=#net2}
N 260 -520 440 -520 {lab=#net2}
N 440 -520 440 -440 {lab=#net2}
N 300 -410 300 -350 {lab=#net2}
N 480 -410 480 -350 {lab=OUT1}
N 300 -580 300 -470 {lab=VDD}
N 300 -580 380 -580 {lab=VDD}
N 380 -580 480 -580 {lab=VDD}
N 480 -580 480 -470 {lab=VDD}
N 390 -200 390 -170 {lab=0}
N 480 -380 520 -380 {lab=OUT1}
N 390 -320 440 -320 {lab=IN1-}
N 300 -320 490 -230 {lab=0}
N 480 -320 490 -320 {lab=0}
N 490 -320 490 -230 {lab=0}
N 390 -230 490 -230 {lab=0}
N 300 -440 380 -440 {lab=VDD}
N 380 -580 380 -440 {lab=VDD}
N 480 -440 530 -440 {lab=VDD}
N 530 -600 530 -440 {lab=VDD}
N 400 -600 530 -600 {lab=VDD}
N 380 -580 400 -600 {lab=VDD}
N 230 -320 260 -320 {lab=IN1+}
N 310 -230 350 -230 {lab=Vbias_tail}
C {sky130_fd_pr/nfet_01v8.sym} 280 -320 0 0 {name=M1
W=4
L=0.5
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 460 -320 0 0 {name=M2
W=4
L=0.5
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 280 -440 0 0 {name=M3
W=8
L=0.5
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 460 -440 0 0 {name=M4
W=8
L=0.5
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 370 -230 0 0 {name=M5
W=6
L=1
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {vdd.sym} 380 -580 0 0 {name=l1 lab=VDD}
C {gnd.sym} 390 -170 0 0 {name=l2 lab=0}
C {ipin.sym} 230 -320 0 0 {name=p1 lab=IN1+}
C {ipin.sym} 420 -320 0 0 {name=p2 lab=IN1-
}
C {opin.sym} 520 -380 0 0 {name=p3 lab=OUT1}
C {ipin.sym} 310 -230 0 0 {name=p4 lab=Vbias_tail}
C {gnd.sym} 490 -230 0 0 {name=l7 lab=0}
