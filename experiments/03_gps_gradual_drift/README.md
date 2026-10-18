# Gps Gradual Drift

Use **gps_gradual_drift.py**: attack, live visuals, automatic checks, chart, summary and recorded review are contained in this one script.

## Results to show

Open [results](results/README.md). This is the single flat evidence folder: original CSV, original metadata, one validation report, one SVG chart, and the matching PNG screenshots. The README explains the result and which screenshots are live or recorded review.

Selected original run: `gps_gradual_drift_20261018T124241_669723Z`. Original CSV and metadata bytes and hashes are unchanged. Previous complete result folders remain under `archive/results_before_simplification_20261018/`.

## Commands

On the university PC (CARLA running, conda carla active):

```bash
cd ~/thesis-gps
python -u gps_gradual_drift.py
```

To check or replay the simplified evidence after copying this experiment folder to a machine with the required environment, run from this folder:

```bash
python gps_gradual_drift.py --check results
python -u gps_gradual_drift.py --replay results
```

New executions still save separate timestamped runs on the university PC to preserve repeatability; this laptop results folder is the single selected evidence set. No driving-controller or VLA response has been tested.
