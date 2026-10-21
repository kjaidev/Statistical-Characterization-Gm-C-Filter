#!/bin/bash
cd ~/projects/gmc-filter
pkill -f streamlit 2>/dev/null
rm -f results_live_* curves_live_* mclive_* netlive_* loglive_* live_err.txt
echo "--- schematics ---"; find . -maxdepth 2 -name "*.sch"
if command -v xschem >/dev/null; then
  for f in $(find . -maxdepth 2 -name "*.sch" | head -6); do (xschem "$f" >/dev/null 2>&1 &); done
else
  echo "xschem not installed here: use the circuit figures in the handbook PDF"
fi
echo "--- netlists ---"; ls *.spice
(sleep 5; cmd.exe /c start http://localhost:8501 >/dev/null 2>&1) &
GMC_FAKE=${GMC_FAKE:-1} streamlit run gmc_app.py --server.headless true
