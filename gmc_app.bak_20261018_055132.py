import os, sys, glob, time, subprocess
import numpy as np, pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

PROJ = os.path.dirname(os.path.abspath(__file__))
FAKE = os.environ.get('GMC_FAKE') == '1'
BLUE, GREEN, RED, AMBER, VIOLET, PINK, CYAN = '#4cc9f0', '#80ed99', '#ff6b6b', '#ffd166', '#b8a1ff', '#f78fb3', '#9bf6ff'
PALETTE = [BLUE, AMBER, GREEN, RED, VIOLET, PINK, CYAN]
GRID = 'rgba(255,255,255,0.08)'
NPTS = 41
CORN, VDDS, TMPS = ['ss', 'tt', 'ff', 'sf', 'fs'], ['1.62', '1.8', '1.98'], ['-20', '27', '85']

def P(*a):
    return os.path.join(PROJ, *a)

def docker_cmd(name, inner):
    return ['docker', 'run', '--rm', '--name', name, '--user', '1000:1000', '-e', 'PATH=/foss/tools/bin:/usr/local/bin:/usr/bin:/bin', '-e', 'HOME=/headless', '-e', 'OMP_NUM_THREADS=1', '--entrypoint', 'bash', '-v', PROJ + ':/foss/designs/gmc-filter', 'hpretl/iic-osic-tools', '-c', 'cd /foss/designs/gmc-filter && ' + inner]

def run_blocking(inner):
    r = subprocess.run(docker_cmd('gmcjob', inner), capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)[-1500:]

def start_job(tag, corner, vdd, temp, n, seed, design='v'):
    if FAKE:
        cmd = [sys.executable, P('fake_sim.py'), tag, str(n)]
    else:
        cmd = docker_cmd('gmclive', './run_live2.sh %s %s_mm %s %s %d %d %s' % (tag, corner, vdd, temp, n, seed, design))
    err = open(P('live_err.txt'), 'w')
    return subprocess.Popen(cmd, stdout=err, stderr=err, cwd=PROJ)

def stop_job(job):
    if FAKE:
        job['proc'].terminate()
    else:
        subprocess.run(['docker', 'stop', 'gmclive'], capture_output=True)

def load_runs(path):
    rows, cur = [], {}
    if not os.path.exists(path):
        return pd.DataFrame()
    for line in open(path):
        p = line.split()
        if len(p) < 3 or p[0] not in ('pw', 'f3', 'f90', 'pk', 'g'):
            continue
        if p[0] == 'pw':
            cur = {}
        try:
            cur[p[0]] = float(p[2])
        except ValueError:
            continue
        if p[0] == 'g' and len(cur) == 5:
            rows.append(cur)
    d = pd.DataFrame(rows)
    if len(d) == 0:
        return d
    u = (d.f3 / d.f90) ** 2
    d['Q'] = 1 / np.sqrt((2 - (1 - u) ** 2) / u)
    d['rip'] = d.pk - d.g
    return d.replace([np.inf, -np.inf], np.nan).dropna()

def load_curves(path):
    if not os.path.exists(path):
        return None
    try:
        a = np.loadtxt(path)
    except Exception:
        return None
    if a.ndim != 2 or a.shape[0] < NPTS:
        return None
    m = a.shape[0] // NPTS
    a = a[:m * NPTS]
    return a[:NPTS, 0], a[:, 1].reshape(m, NPTS), a[:, -1].reshape(m, NPTS) * 180 / np.pi

def stats(d, tgt, tol, qlo, qhi):
    ok = (abs(d.f3 / tgt - 1) <= tol) & (d.Q >= qlo) & (d.Q <= qhi)
    m = d.f3.mean()
    return dict(n=len(d), f3=m / 1e6, f3sd=100 * d.f3.std() / m, Q=d.Q.mean(), Qsd=d.Q.std(), P=d.pw.mean() * 1e6, Psd=100 * d.pw.std() / d.pw.mean(), rip=d.rip.mean(), yld=100 * ok.mean())

def style(fig, h=300, title=None):
    fig.update_layout(template='plotly_dark', height=h, margin=dict(l=45, r=15, t=50 if title else 40, b=40), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=(dict(orientation='h', y=1.02, yanchor='bottom', x=1, xanchor='right') if title else dict(orientation='h', y=1.14, x=0)), title=dict(text=title, font=dict(size=14)) if title else None)
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig

def hist_fig(x, title, color, spec=None):
    x = np.asarray(x)
    m, s = x.mean(), x.std()
    fig = go.Figure(go.Histogram(x=x, nbinsx=30, marker_color=color, opacity=0.85, name='runs'))
    if spec:
        fig.add_vrect(x0=spec[0], x1=spec[1], fillcolor='rgba(128,237,153,0.12)', line_width=0)
    if len(x) > 5 and s > 0:
        g = np.linspace(m - 4 * s, m + 4 * s, 120)
        bw = (x.max() - x.min()) / 30 or 1.0
        fig.add_trace(go.Scatter(x=g, y=len(x) * bw * np.exp(-0.5 * ((g - m) / s) ** 2) / (s * np.sqrt(2 * np.pi)), mode='lines', line=dict(color=AMBER, width=2), name='normal fit'))
    fig.add_vline(x=m, line_dash='dash', line_color='white', opacity=0.6)
    fig.update_layout(showlegend=False, bargap=0.05)
    return style(fig, 280, '%s   %.4g ± %.3g' % (title, m, s))

def bode_fig(cur, maxc=250):
    f, mag, ph = cur
    m = mag.shape[0]
    idx = np.arange(m) if m <= maxc else np.linspace(0, m - 1, maxc).astype(int)
    fig = make_subplots(rows=1, cols=3, subplot_titles=('Magnitude (dB)', 'Cutoff region (zoom)', 'Phase (deg)'), horizontal_spacing=0.07)
    X = np.tile(np.append(f, np.nan), len(idx)) / 1e6
    for col in (1, 2, 3):
        arr = ph if col == 3 else mag
        Y = np.concatenate([np.append(arr[i], np.nan) for i in idx])
        fig.add_trace(go.Scatter(x=X, y=Y, mode='lines', line=dict(color=BLUE, width=1), opacity=0.2, showlegend=False, hoverinfo='skip'), row=1, col=col)
        mu, sd = arr.mean(0), arr.std(0)
        fig.add_trace(go.Scatter(x=f / 1e6, y=mu + 3 * sd, mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=col)
        fig.add_trace(go.Scatter(x=f / 1e6, y=mu - 3 * sd, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(255,209,102,0.20)', showlegend=False, hoverinfo='skip'), row=1, col=col)
        fig.add_trace(go.Scatter(x=f / 1e6, y=mu, mode='lines', line=dict(color=AMBER, width=2.5), name='mean', showlegend=False), row=1, col=col)
    fig.add_hline(y=-3, line_dash='dot', line_color=RED, row=1, col=1)
    fig.add_hline(y=-3, line_dash='dot', line_color=RED, row=1, col=2)
    fig.add_hline(y=-90, line_dash='dot', line_color=RED, row=1, col=3)
    fig.update_xaxes(type='log', title_text='MHz')
    fig.update_xaxes(range=[np.log10(0.9), np.log10(3.5)], row=1, col=2)
    fig.update_yaxes(range=[-8, 1], row=1, col=2)
    return style(fig, 340)

def scatter_fig(d, tgt, tol, qlo, qhi):
    ok = (abs(d.f3 / tgt - 1) <= tol) & (d.Q >= qlo) & (d.Q <= qhi)
    fig = go.Figure()
    for flag, color, name in ((True, GREEN, 'in spec'), (False, RED, 'out of spec')):
        s = d[ok == flag]
        fig.add_trace(go.Scattergl(x=s.f3 / 1e6, y=s.Q, mode='markers', marker=dict(color=color, size=5, opacity=0.7), name=name))
    fig.add_shape(type='rect', x0=tgt * (1 - tol) / 1e6, x1=tgt * (1 + tol) / 1e6, y0=qlo, y1=qhi, line=dict(color=GREEN, dash='dot'))
    fig.update_xaxes(title_text='f3 (MHz)')
    fig.update_yaxes(title_text='Q')
    return style(fig, 300, 'f3 vs Q (dotted box = spec)')

def conv_fig(d):
    k = np.arange(1, len(d) + 1)
    rm = d.f3.expanding().mean() / 1e6
    rs = 100 * d.f3.expanding().std() / d.f3.expanding().mean()
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Scatter(x=k, y=rm, name='running mean f3 (MHz)', line=dict(color=BLUE)), secondary_y=False)
    fig.add_trace(go.Scatter(x=k, y=rs, name='running σ (%)', line=dict(color=AMBER)), secondary_y=True)
    fig.update_xaxes(title_text='runs')
    return style(fig, 300, 'Convergence of the estimates')

def kpi_row(d, s, el, n):
    rate = len(d) / el if el > 0 else 0
    eta = (n - len(d)) / rate if rate > 0 else 0
    c = st.columns(6)
    c[0].metric('runs', '%d / %d' % (len(d), n), '%.1f runs/s, ETA %.0fs' % (rate, eta), delta_color='off', delta_arrow='off')
    c[1].metric('f3 (MHz)', '%.3f' % s['f3'], 'σ = %.2f%%' % s['f3sd'], delta_color='off', delta_arrow='off')
    c[2].metric('Q', '%.3f' % s['Q'], 'σ = %.3f' % s['Qsd'], delta_color='off', delta_arrow='off')
    c[3].metric('power (µW)', '%.1f' % s['P'], 'σ = %.2f%%' % s['Psd'], delta_color='off', delta_arrow='off')
    c[4].metric('ripple (dB)', '%.3f' % s['rip'])
    c[5].metric('yield', '%.1f%%' % s['yld'])

def live_panel(job, spec):
    tgt, tol, qlo, qhi = spec
    running = job['proc'].poll() is None
    if not running and 'tend' not in job:
        job['tend'] = time.time()
    el = job.get('tend', time.time()) - job['t0']
    d = load_runs(P('results_%s.txt' % job['tag']))
    n = job['n']
    st.progress(min(len(d) / n, 1.0), text=('running' if running else 'finished') + ' · %s · %d / %d runs' % (job['tag'], len(d), n))
    if len(d) < 3:
        if running:
            st.info('Waiting for the first results (loading the PDK takes a few seconds)...')
        else:
            st.error('Job ended without results.')
            if os.path.exists(P('live_err.txt')):
                st.code(open(P('live_err.txt')).read()[-1200:] or '(no output)')
    else:
        s = stats(d, tgt, tol, qlo, qhi)
        kpi_row(d, s, el, n)
        cur = load_curves(P('curves_%s.txt' % job['tag']))
        if cur is not None:
            st.plotly_chart(bode_fig(cur), width='stretch')
            st.caption('Blue = individual runs · yellow = mean with ±3σ band · red dotted = −3 dB and −90° references')
        else:
            st.caption('Frequency-response curves not available for this job.')
        c = st.columns(3)
        c[0].plotly_chart(hist_fig(d.f3 / 1e6, 'f3 (MHz)', BLUE, (tgt * (1 - tol) / 1e6, tgt * (1 + tol) / 1e6)), width='stretch')
        c[1].plotly_chart(hist_fig(d.Q, 'Q', VIOLET, (qlo, qhi)), width='stretch')
        c[2].plotly_chart(hist_fig(d.pw * 1e6, 'power (µW)', GREEN), width='stretch')
        c = st.columns(2)
        c[0].plotly_chart(scatter_fig(d, tgt, tol, qlo, qhi), width='stretch')
        c[1].plotly_chart(conv_fig(d), width='stretch')
    if not running and not job.get('final'):
        job['final'] = True
        st.rerun()

def render_live(job, spec):
    run_every = 1.0 if job['proc'].poll() is None else None
    st.fragment(run_every=run_every)(live_panel)(job, spec)

def grid_running(pfx='g'):
    fs = glob.glob(P('results_%s_*.txt' % pfx))
    return bool(fs) and max(os.path.getmtime(f) for f in fs) > time.time() - 20

def pvt_panel(spec, pfx='g'):
    tgt, tol, qlo, qhi = spec
    rows = []
    for c in CORN:
        for v in VDDS:
            for t in TMPS:
                d = load_runs(P('results_%s_%s_%s_%s.txt' % (pfx, c, v, t)))
                if len(d) > 2:
                    r = stats(d, tgt, tol, qlo, qhi)
                    r.update(corner=c, vdd=v, T=t)
                    rows.append(r)
    if not rows:
        st.info('No grid results yet (results_%s_*.txt).' % pfx + '')
        return
    df = pd.DataFrame(rows)
    st.progress(len(df) / 45, text='%d / 45 conditions with data · %d runs total%s' % (len(df), df.n.sum(), ' · sweep running' if grid_running(pfx) else ''))
    labels = {'Mean f3 (MHz)': ('f3', 'Viridis'), 'f3 spread σ (%)': ('f3sd', 'Magma'), 'Mean Q': ('Q', 'Viridis'), 'Mean power (µW)': ('P', 'Cividis'), 'Yield vs spec (%)': ('yld', 'RdYlGn'), 'Ripple (dB)': ('rip', 'Viridis')}
    pick = st.radio('Metric', list(labels), horizontal=True)
    key, scale = labels[pick]
    fig = make_subplots(rows=1, cols=5, shared_yaxes=True, subplot_titles=[c.upper() for c in CORN], horizontal_spacing=0.025)
    lo, hi = df[key].min(), df[key].max()
    for i, c in enumerate(CORN):
        Z = np.full((3, 3), np.nan)
        for a, v in enumerate(VDDS):
            for b, t in enumerate(TMPS):
                x = df[(df.corner == c) & (df.vdd == v) & (df['T'] == t)]
                if len(x):
                    Z[a, b] = x[key].iloc[0]
        fig.add_trace(go.Heatmap(z=Z, x=TMPS, y=VDDS, zmin=lo, zmax=hi, colorscale=scale, texttemplate='%{z:.2f}', xgap=3, ygap=3, showscale=(i == 4), colorbar=dict(thickness=10)), row=1, col=i + 1)
    fig.update_xaxes(type='category', title_text='T (°C)')
    fig.update_yaxes(type='category')
    fig.update_yaxes(title_text='VDD (V)', row=1, col=1)
    st.plotly_chart(style(fig, 300), width='stretch')
    c1, c2 = st.columns(2)
    vsel = c1.selectbox('f3 vs temperature at VDD =', VDDS, index=1)
    tsel = c2.selectbox('f3 vs VDD at T (°C) =', TMPS, index=1)
    f1, f2 = go.Figure(), go.Figure()
    for i, c in enumerate(CORN):
        s1 = df[(df.corner == c) & (df.vdd == vsel)].copy()
        s1['t'] = s1['T'].astype(float)
        s1 = s1.sort_values('t')
        f1.add_trace(go.Scatter(x=s1.t, y=s1.f3, error_y=dict(type='data', array=s1.f3 * s1.f3sd / 100), mode='lines+markers', name=c, line=dict(color=PALETTE[i])))
        s2 = df[(df.corner == c) & (df['T'] == tsel)].copy()
        s2['v'] = s2.vdd.astype(float)
        s2 = s2.sort_values('v')
        f2.add_trace(go.Scatter(x=s2.v, y=s2.f3, error_y=dict(type='data', array=s2.f3 * s2.f3sd / 100), mode='lines+markers', name=c, line=dict(color=PALETTE[i])))
    f1.add_hline(y=tgt / 1e6, line_dash='dot', line_color='white')
    f2.add_hline(y=tgt / 1e6, line_dash='dot', line_color='white')
    f1.update_xaxes(title_text='temperature (°C)')
    f2.update_xaxes(title_text='VDD (V)')
    f1.update_yaxes(title_text='f3 (MHz), bars = ±1σ')
    f2.update_yaxes(title_text='f3 (MHz), bars = ±1σ')
    c1.plotly_chart(style(f1, 320), width='stretch')
    c2.plotly_chart(style(f2, 320), width='stretch')
    show = df[['corner', 'vdd', 'T', 'n', 'f3', 'f3sd', 'Q', 'Qsd', 'P', 'Psd', 'rip', 'yld']].rename(columns={'vdd': 'VDD', 'f3': 'f3 MHz', 'f3sd': 'f3 σ%', 'Qsd': 'Q σ', 'P': 'P µW', 'Psd': 'P σ%', 'rip': 'ripple dB', 'yld': 'yield %'}).round(3)
    st.dataframe(show, hide_index=True)

def render_pvt(spec, pfx='g'):
    st.fragment(run_every=3.0 if grid_running(pfx) else None)(pvt_panel)(spec, pfx)

st.set_page_config(page_title='Gm-C SKY130 lab', layout='wide')
st.title('Gm-C filter in SKY130: live Monte Carlo and PVT lab')
st.sidebar.header('Spec')
tgt = st.sidebar.number_input('target f3 (MHz)', 0.5, 5.0, 1.6, 0.05) * 1e6
tol = st.sidebar.slider('f3 tolerance (± %)', 1, 30, 10) / 100
qlo, qhi = st.sidebar.slider('Q window', 0.3, 1.2, (0.6, 0.8))
spec = (tgt, tol, qlo, qhi)
tabs = st.tabs(['Live Monte Carlo', 'PVT grid', 'Compare sets', 'Pelgrom', 'Transient', 'Bias comparison', 'Study results'])

with tabs[0]:
    DES = {'Voltage bias (baseline)': 'v', 'PTAT current bias (final)': 'pt', 'PTAT, x4 mirror': 'pt4'}
    dname = st.radio('Design', list(DES), index=1, horizontal=True)
    c = st.columns([1, 1, 1, 1, 1, 1.4])
    corner = c[0].selectbox('corner', ['tt', 'ss', 'ff', 'sf', 'fs'])
    vdd = c[1].number_input('VDD (V)', 1.4, 2.2, 1.8, 0.01)
    temp = c[2].number_input('temp (°C)', -40, 125, 27)
    n = c[3].number_input('MC runs', 10, 5000, 300, 50)
    seed = c[4].number_input('seed', 1, 999999, 12345)
    job = st.session_state.get('job')
    running = job is not None and job['proc'].poll() is None
    b1, b2 = c[5].columns(2)
    if b1.button('Run', type='primary', disabled=running):
        tag = 'live_%s_%s_%s_%s' % (DES[dname], corner, vdd, temp)
        st.session_state['job'] = dict(proc=start_job(tag, corner, vdd, temp, int(n), int(seed), DES[dname]), tag=tag, n=int(n), t0=time.time())
        st.rerun()
    if b2.button('Stop', disabled=not running):
        stop_job(job)
        st.rerun()
    if job is not None:
        render_live(job, spec)
    else:
        st.info('Pick a condition and press Run. Every plot updates live as runs complete.')

with tabs[1]:
    DS = {'PTAT current bias (final)': 'pt', 'Voltage bias (baseline)': 'g'}
    pname = st.radio('Dataset', list(DS), horizontal=True, key='pvtds')
    render_pvt(spec, DS[pname])

with tabs[2]:
    names = sorted(os.path.basename(f)[8:-4] for f in glob.glob(P('results_*.txt')))
    sel = st.multiselect('Result sets to overlay', names, default=[x for x in ('nom', 'ss', 'ff') if x in names])
    if sel:
        data = {k: load_runs(P('results_%s.txt' % k)) for k in sel}
        data = {k: v for k, v in data.items() if len(v) > 2}
        c = st.columns(3)
        for col, (key, lab, sc) in zip(c, [('f3', 'f3 (MHz)', 1e-6), ('Q', 'Q', 1), ('pw', 'power (µW)', 1e6)]):
            fig = go.Figure()
            for i, (k, v) in enumerate(data.items()):
                fig.add_trace(go.Histogram(x=v[key] * sc, name=k, opacity=0.6, nbinsx=40, marker_color=PALETTE[i % len(PALETTE)]))
            fig.update_layout(barmode='overlay')
            fig.update_xaxes(title_text=lab)
            col.plotly_chart(style(fig, 300), width='stretch')
        fig = go.Figure()
        for i, (k, v) in enumerate(data.items()):
            fig.add_trace(go.Box(y=v.f3 / 1e6, name=k, marker_color=PALETTE[i % len(PALETTE)], boxmean='sd'))
        fig.update_yaxes(title_text='f3 (MHz)')
        st.plotly_chart(style(fig, 320, 'f3 distributions'), width='stretch')
        tb = pd.DataFrame([dict(stats(v, *spec), set=k) for k, v in data.items()])
        st.dataframe(tb[['set', 'n', 'f3', 'f3sd', 'Q', 'Qsd', 'P', 'Psd', 'rip', 'yld']].round(3), hide_index=True)

with tabs[3]:
    if st.button('Re-run Pelgrom bench (500 samples)'):
        with st.spinner('Running...'):
            run_blocking('rm -f pelgrom_out.txt; ngspice -b pelgrom.cir > pelgrom_log.txt 2>&1')
    f = P('pelgrom_out.txt')
    if os.path.exists(f):
        v = {k: [] for k in ['d1', 'd2', 'd3', 'd4']}
        for line in open(f):
            p = line.split()
            if len(p) >= 3 and p[0] in v:
                v[p[0]].append(float(p[2]))
        wl = np.array([0.5, 2, 8, 32])
        sim = np.array([1e3 * np.std(v[k]) for k in v])
        x = np.logspace(-0.4, 1.6, 60)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=wl, y=sim, mode='markers', marker=dict(size=11, color=BLUE), name='simulated σ(ΔVgs)'))
        fig.add_trace(go.Scatter(x=x, y=np.sqrt(2) * 3.356 / np.sqrt(x), mode='lines', line=dict(color=AMBER, dash='dash'), name='hand-calc √2·A_VT/√(WL), A_VT = 3.356 mV·µm'))
        fig.update_xaxes(type='log', title_text='W·L (µm²)')
        fig.update_yaxes(type='log', title_text='σ (mV)')
        st.plotly_chart(style(fig, 380, 'Pelgrom matching check'), width='stretch')
        st.dataframe(pd.DataFrame({'WL (µm²)': wl, 'simulated σ (mV)': sim.round(3), 'hand-calc (mV)': (np.sqrt(2) * 3.356 / np.sqrt(wl)).round(3), 'ratio': (sim / (np.sqrt(2) * 3.356 / np.sqrt(wl))).round(2)}), hide_index=True)
    else:
        st.info('pelgrom_out.txt not found')

with tabs[4]:
    if st.button('Re-run transient'):
        with st.spinner('Running...'):
            run_blocking('ngspice -b net_tran.spice > log_tran.txt 2>&1')
    f = P('tran_out.txt')
    if os.path.exists(f):
        x = np.loadtxt(f)
        t_, v_ = x[:, 0] * 1e9, x[:, 1] * 1e3
        vi = v_[(t_ >= 50) & (t_ <= 100)].mean()
        vf = v_[t_ >= 3500].mean() if t_.max() >= 3500 else v_[-20:].mean()
        seg = t_ >= 100
        ip = np.argmax(np.where(seg, v_, -1e9))
        c = st.columns(3)
        c[0].metric('overshoot', '%.2f %%' % (100 * (v_[ip] - vf) / (vf - vi)))
        c[1].metric('peak time after step', '%.0f ns' % (t_[ip] - 100))
        c[2].metric('step size', '%.2f mV' % (vf - vi))
        fig = go.Figure(go.Scatter(x=t_, y=v_, mode='lines', line=dict(color=BLUE, width=2.5), name='vo2'))
        fig.add_hline(y=vf, line_dash='dot', line_color=GREEN, annotation_text='final value')
        fig.add_trace(go.Scatter(x=[t_[ip]], y=[v_[ip]], mode='markers', marker=dict(size=11, color=AMBER), name='peak'))
        fig.update_xaxes(title_text='time (ns)', range=[0, 1500])
        fig.update_yaxes(title_text='vo2 (mV)')
        st.plotly_chart(style(fig, 380, 'Step response (10 mV input step at 100 ns)'), width='stretch')
    else:
        st.info('tran_out.txt not found')


def grid_df(pfx, spec):
    tgt, tol, qlo, qhi = spec
    rows = []
    for c in CORN:
        for v in VDDS:
            for t in TMPS:
                d = load_runs(P('results_%s_%s_%s_%s.txt' % (pfx, c, v, t)))
                if len(d) > 2:
                    r = stats(d, tgt, tol, qlo, qhi)
                    r.update(corner=c, vdd=v, T=t)
                    rows.append(r)
    return pd.DataFrame(rows)

with tabs[5]:
    a, b = grid_df('g', spec), grid_df('pt', spec)
    if len(a) == 0 or len(b) == 0:
        st.info('Needs both results_g_*.txt (voltage bias) and results_pt_*.txt (PTAT).')
    else:
        m = a.merge(b, on=['corner', 'vdd', 'T'], suffixes=('_v', '_p'))
        k = st.columns(4)
        k[0].metric('Conditions compared', len(m))
        k[1].metric('Mean yield, voltage bias', '%.1f%%' % m.yld_v.mean())
        k[2].metric('Mean yield, PTAT', '%.1f%%' % m.yld_p.mean(), '%+.1f pts' % (m.yld_p.mean() - m.yld_v.mean()))
        k[3].metric('Worst f3 shift from target (MHz)', '%.2f -> %.2f' % ((m.f3_v - tgt / 1e6).abs().max(), (m.f3_p - tgt / 1e6).abs().max()), delta_color='off', delta_arrow='off')
        m['lab'] = m.corner + ' ' + m.vdd + 'V ' + m['T'] + 'C'
        f = go.Figure()
        f.add_trace(go.Bar(x=m.lab, y=m.f3_v, name='voltage bias', marker_color=AMBER))
        f.add_trace(go.Bar(x=m.lab, y=m.f3_p, name='PTAT', marker_color=BLUE))
        f.add_hline(y=tgt / 1e6, line_dash='dot', line_color='white')
        f.update_yaxes(title_text='mean f3 (MHz)')
        f.update_layout(barmode='group')
        st.plotly_chart(style(f, 340), width='stretch')
        g = go.Figure()
        g.add_trace(go.Bar(x=m.lab, y=m.yld_v, name='voltage bias', marker_color=AMBER))
        g.add_trace(go.Bar(x=m.lab, y=m.yld_p, name='PTAT', marker_color=BLUE))
        g.update_yaxes(title_text='yield (%)')
        g.update_layout(barmode='group')
        st.plotly_chart(style(g, 340), width='stretch')
        by = m.groupby('corner')[['yld_v', 'yld_p']].mean().round(1).rename(columns={'yld_v': 'yield % voltage', 'yld_p': 'yield % PTAT'})
        st.dataframe(by)

with tabs[6]:
    st.caption('Analysis outputs from the study (a*_out.txt in the project folder) and the extra Monte Carlo sets.')
    extra = [('results_pt_s2_tt_1.8_27', 'PTAT, tt 1.8 V 27 C, 1500 runs, seed 54321'), ('results_pt_s2_sf_1.62_-20', 'PTAT, sf 1.62 V -20 C, 1500 runs, seed 54321'), ('results_pt_tight_tt_1.8_27', 'PTAT tight, tt 1.8 V 27 C, 300 runs'),
             ('results_ptm_m1_tt_1.8_27', 'mirror x1, tt 27 C'), ('results_ptm_m4_tt_1.8_27', 'mirror x4, tt 27 C'), ('results_ptm_m16_tt_1.8_27', 'mirror x16, tt 27 C'),
             ('results_ptm_m1_tt_1.8_-20', 'mirror x1, tt -20 C'), ('results_ptm_m4_tt_1.8_-20', 'mirror x4, tt -20 C'), ('results_ptm_m16_tt_1.8_-20', 'mirror x16, tt -20 C')]
    rows = []
    for fn, lab in extra:
        d = load_runs(P(fn + '.txt'))
        if len(d) > 2:
            r = stats(d, tgt, tol, qlo, qhi)
            rows.append({'set': lab, 'n': r['n'], 'f3 MHz': r['f3'], 'f3 sigma %': r['f3sd'], 'Q': r['Q'], 'Q sigma': r['Qsd'], 'P uW': r['P'], 'yield %': r['yld']})
    if rows:
        st.dataframe(pd.DataFrame(rows).round(3), hide_index=True)
    for f in sorted(glob.glob(P('a*_out.txt'))):
        with st.expander(os.path.basename(f)):
            st.code(open(f).read()[-6000:])
