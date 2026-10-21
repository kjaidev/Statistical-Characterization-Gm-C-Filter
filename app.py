import os, subprocess, glob, time
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import streamlit as st

PROJ = os.path.dirname(os.path.abspath(__file__))
F0 = 1.6e6
DOCKER = ['docker', 'run', '--rm', '--user', '1000:1000', '-e', 'PATH=/foss/tools/bin:/usr/local/bin:/usr/bin:/bin', '-e', 'HOME=/headless', '-e', 'OMP_NUM_THREADS=1', '--entrypoint', 'bash', '-v', PROJ + ':/foss/designs/gmc-filter', 'hpretl/iic-osic-tools', '-c']

def in_container(cmd):
    r = subprocess.run(DOCKER + ['cd /foss/designs/gmc-filter && ' + cmd], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)[-1500:]

def load(path):
    rows, cur = [], {}
    for line in open(path):
        p = line.split()
        if len(p) < 3 or p[0] not in ('pw', 'f3', 'f90', 'pk', 'g'):
            continue
        if p[0] == 'pw':
            cur = {}
        cur[p[0]] = float(p[2])
        if p[0] == 'g' and len(cur) == 5:
            rows.append(cur)
    d = pd.DataFrame(rows)
    if len(d) == 0:
        return d
    u = (d.f3 / d.f90) ** 2
    d['Q'] = 1 / np.sqrt((2 - (1 - u) ** 2) / u)
    d['rip'] = d.pk - d.g
    return d

def stats(d, ftol, qlo, qhi):
    ok = (abs(d.f3 / F0 - 1) <= ftol) & (d.Q >= qlo) & (d.Q <= qhi)
    return dict(n=len(d), f3=d.f3.mean() / 1e6, f3sd=100 * d.f3.std() / d.f3.mean(), Q=d.Q.mean(), Qsd=d.Q.std(), P=d.pw.mean() * 1e6, rip=d.rip.mean(), yld=100 * ok.mean())

def hists(d):
    fig, ax = plt.subplots(1, 4, figsize=(13, 3))
    for a, col, sc, lab in zip(ax, ['f3', 'Q', 'pw', 'rip'], [1e-6, 1, 1e6, 1], ['f3 (MHz)', 'Q', 'power (uW)', 'ripple (dB)']):
        a.hist(d[col] * sc, bins=30)
        a.set_xlabel(lab)
    plt.tight_layout()
    return fig

def show(d, ftol, qlo, qhi):
    if len(d) < 3:
        st.warning('Not enough complete runs yet')
        return
    s = stats(d, ftol, qlo, qhi)
    c = st.columns(6)
    c[0].metric('runs', s['n'])
    c[1].metric('f3 (MHz)', '%.3f' % s['f3'], '%.2f%% sd' % s['f3sd'], delta_color='off')
    c[2].metric('Q', '%.3f' % s['Q'], '%.3f sd' % s['Qsd'], delta_color='off')
    c[3].metric('power (uW)', '%.1f' % s['P'])
    c[4].metric('ripple (dB)', '%.3f' % s['rip'])
    c[5].metric('yield (%)', '%.1f' % s['yld'])
    st.pyplot(hists(d))

st.set_page_config(page_title='Gm-C SKY130 simulator', layout='wide')
st.title('Gm-C filter: SKY130 Monte Carlo / PVT')
ftol = st.sidebar.slider('f3 tolerance (+/- %) around 1.6 MHz', 1, 30, 10) / 100
qlo, qhi = st.sidebar.slider('Q window', 0.3, 1.2, (0.6, 0.8))
tabs = st.tabs(['Run simulation', 'Browse results', 'PVT map', 'Pelgrom', 'Transient'])

with tabs[0]:
    c = st.columns(4)
    corner = c[0].selectbox('corner', ['tt', 'ss', 'ff', 'sf', 'fs'])
    vdd = c[1].number_input('VDD (V)', 1.4, 2.2, 1.8, 0.01)
    temp = c[2].number_input('temp (C)', -40, 125, 27)
    n = c[3].number_input('MC runs', 3, 2000, 200, 50)
    if st.button('Run'):
        tag = 'app_%s_%s_%s' % (corner, vdd, temp)
        t0 = time.time()
        with st.spinner('Simulating %d runs ...' % n):
            rc, out = in_container('./run_sweep.sh %s %s_mm %s %s %d' % (tag, corner, vdd, temp, n))
        if rc == 0:
            st.success('done in %.0f s' % (time.time() - t0))
        else:
            st.error(out)
        st.session_state['last'] = tag
    if 'last' in st.session_state:
        f = os.path.join(PROJ, 'results_%s.txt' % st.session_state['last'])
        if os.path.exists(f):
            show(load(f), ftol, qlo, qhi)

with tabs[1]:
    files = sorted(glob.glob(os.path.join(PROJ, 'results_*.txt')))
    names = [os.path.basename(f)[8:-4] for f in files]
    if names:
        pick = st.selectbox('results set', names)
        show(load(os.path.join(PROJ, 'results_%s.txt' % pick)), ftol, qlo, qhi)
    else:
        st.info('No results files found')

with tabs[2]:
    CORN, VDD, TMP = ['ss', 'tt', 'ff', 'sf', 'fs'], ['1.62', '1.8', '1.98'], ['-20', '27', '85']
    rows = []
    for c_ in CORN:
        for v in VDD:
            for t in TMP:
                f = os.path.join(PROJ, 'results_g_%s_%s_%s.txt' % (c_, v, t))
                if os.path.exists(f):
                    d = load(f)
                    if len(d) > 2:
                        r = stats(d, ftol, qlo, qhi)
                        r.update(corner=c_, vdd=v, T=t)
                        rows.append(r)
    if rows:
        df = pd.DataFrame(rows)
        st.caption('%d of 45 conditions available' % len(df))
        key = st.selectbox('metric', ['f3', 'f3sd', 'Q', 'P', 'rip', 'yld'])
        fig, ax = plt.subplots(1, 5, figsize=(15, 3.2), sharey=True)
        lo, hi = df[key].min(), df[key].max()
        for a, c_ in zip(ax, CORN):
            M = np.full((3, 3), np.nan)
            for i, v in enumerate(VDD):
                for j, t in enumerate(TMP):
                    x = df[(df.corner == c_) & (df.vdd == v) & (df['T'] == t)]
                    if len(x):
                        M[i, j] = x[key].iloc[0]
            a.imshow(M, vmin=lo, vmax=hi, cmap='viridis', aspect='auto')
            a.set_title(c_)
            a.set_xticks(range(3))
            a.set_xticklabels(TMP)
            a.set_xlabel('T (C)')
            for i in range(3):
                for j in range(3):
                    if not np.isnan(M[i, j]):
                        a.text(j, i, '%.2f' % M[i, j], ha='center', va='center', color='w', fontsize=8)
        ax[0].set_yticks(range(3))
        ax[0].set_yticklabels(VDD)
        ax[0].set_ylabel('VDD (V)')
        plt.tight_layout()
        st.pyplot(fig)
        st.dataframe(df)
    else:
        st.info('Grid results not found yet')

with tabs[3]:
    img = os.path.join(PROJ, 'fig_pelgrom_handcalc.png')
    if os.path.exists(img):
        st.image(img, width=500)
    if st.button('Re-run Pelgrom bench (500 samples)'):
        with st.spinner('Running ...'):
            in_container('rm -f pelgrom_out.txt; ngspice -b pelgrom.cir > pelgrom_log.txt 2>&1')
    f = os.path.join(PROJ, 'pelgrom_out.txt')
    if os.path.exists(f):
        v = {k: [] for k in ['d1', 'd2', 'd3', 'd4']}
        for line in open(f):
            p = line.split()
            if len(p) >= 3 and p[0] in v:
                v[p[0]].append(float(p[2]))
        wl = [0.5, 2, 8, 32]
        st.dataframe(pd.DataFrame({'WL (um2)': wl, 'sigma dVgs (mV)': [1e3 * np.std(v[k]) for k in v], 'hand-calc (mV)': [1.414 * 3.356 / np.sqrt(w) for w in wl]}))

with tabs[4]:
    if st.button('Re-run transient'):
        with st.spinner('Running ...'):
            in_container('ngspice -b net_tran.spice > log_tran.txt 2>&1')
    f = os.path.join(PROJ, 'tran_out.txt')
    if os.path.exists(f):
        x = np.loadtxt(f)
        t_, v_ = x[:, 0] * 1e9, x[:, 1] * 1e3
        vi = v_[(t_ >= 50) & (t_ <= 100)].mean()
        vf = v_[t_ >= 3500].mean() if t_.max() >= 3500 else v_[-20:].mean()
        st.metric('overshoot (%)', '%.2f' % (100 * (v_[t_ >= 100].max() - vf) / (vf - vi)))
        fig, a = plt.subplots(figsize=(7, 3.5))
        a.plot(t_, v_)
        a.set_xlim(0, 1500)
        a.set_xlabel('time (ns)')
        a.set_ylabel('vo2 (mV)')
        a.grid(alpha=0.3)
        st.pyplot(fig)
