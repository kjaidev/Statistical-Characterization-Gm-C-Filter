BLOCK = "\n    try:\n        st.markdown('#### Transistor-level bias core (beta-multiplier), 45 conditions x 40 runs')\n        fp = P('ptat_mc_summary.txt')\n        if os.path.exists(fp):\n            tdf = pd.read_csv(fp, sep=r'\\s+')\n            tdf['vdd'] = tdf['vdd'].astype(str)\n            ys = tdf.yield_pct\n            c1, c2, c3, c4 = st.columns(4)\n            c1.metric('mean yield', '%.1f %%' % ys.mean())\n            c2.metric('worst condition', '%.1f %%' % ys.min())\n            c3.metric('best condition', '%.1f %%' % ys.max())\n            c4.metric('worst mean f3 error', '%.3f MHz' % (tdf.f3_mean - 1.6).abs().max())\n            cs = ['tt', 'ss', 'ff', 'sf', 'fs']\n            cols = [(v, t) for v in ['1.62', '1.8', '1.98'] for t in [-20, 27, 85]]\n            M = np.array([[tdf[(tdf.corner == c) & (tdf.vdd == v) & (tdf['T'] == t)].yield_pct.iloc[0] for v, t in cols] for c in cs])\n            fig = go.Figure(go.Heatmap(z=M, x=['%s V, %d C' % (v, t) for v, t in cols], y=cs, text=M.round(0).astype(int).astype(str), texttemplate='%{text}', colorscale='Blues', zmin=0, zmax=100, colorbar=dict(title='yield %')))\n            st.plotly_chart(style(fig, 330), width='stretch')\n            st.caption('Voltage bias 22.4 %, ideal PTAT source 88.7 %, transistor-level core as above. With 40 runs per condition the mean is good to about +/-2 points and a single cell to about +/-15.')\n            st.dataframe(tdf.round(4), hide_index=True)\n        else:\n            st.info('ptat_mc_summary.txt not found (run ptat_mc.py).')\n    except Exception as e:\n        st.warning('This section could not be drawn: %r' % (e,))\n"
fn = 'gmc_app.py'
import os, shutil, time, sys
s = open(fn).read()
if 'Transistor-level bias core' in s:
    print('already patched'); sys.exit(0)
if 'Cross-checks and limits' not in s:
    print('apply patch_webpage.py first'); sys.exit(1)
shutil.copy(fn, 'gmc_app.bak2_%s.py' % time.strftime('%Y%m%d_%H%M%S'))
old = 'so 88.7 % yield is an upper bound.'
if old in s:
    s = s.replace(old, 'so 88.7 % yield is an upper bound (a transistor-level core gives 71.7 %, shown above).')
else:
    print('note: limits line not found, left unchanged')
s = s.rstrip('\n') + '\n' + BLOCK
open(fn, 'w').write(s)
print('patched OK')
