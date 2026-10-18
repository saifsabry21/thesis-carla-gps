# Thesis CARLA GPS experiments

Start with [setup/START_HERE.md](setup/START_HERE.md). Each attack has one active script containing the attack, live visuals, automatic checks, chart, summary and recorded review.

| Experiment | Active script | Latest documented result |
|---|---|---|
| [Baseline](experiments/01_gps_baseline/README.md) | gps_baseline.py | 100 original readings archived |
| [Fixed offset](experiments/02_gps_fixed_offset/README.md) | gps_fixed_offset.py | +5 m; 51 clean / 49 attack; 14 checks passed |
| [Gradual drift](experiments/03_gps_gradual_drift/README.md) | gps_gradual_drift.py | 0→10 m; 51 clean / 100 drift / 49 hold; 14 checks passed |
| [Dropout](experiments/04_gps_dropout/README.md) | gps_dropout.py | 50 clean / 50 withheld / 50 recovery; 13 checks passed |

Each experiment now has one flat `results/` folder containing only the selected evidence. There are no timestamped subfolders inside the active results folder. Keep the original CSV, original metadata, one validation report, one SVG chart and matching screenshots; the baseline instead keeps its original CSV and execution output. See each results/README.md for provenance.

For dropout, the selected evidence is the earlier verified recording that matches the colored screenshots. The later combined-script run is safely archived. Fixed offset and drift retain the verified combined-script runs and their matching screenshots.

All previous complete result folders are preserved under each experiment's archive/results_before_simplification_20261018/. No raw data or screenshots were discarded. Archived files are historical evidence and not required for showing the selected result.

The physical vehicle remained parked. These experiments manipulate the Python-reported GPS output; they do not transmit RF interference or establish controller/VLA attack success. The next stage is to connect attacked output to a consumer and evaluate its response.

Old scripts and earlier visual fixed-offset evidence remain in experiment archives. Setup transfer ZIPs contain copies of the active scripts for convenience. The full inbound result snapshot is in archive/backups/university_results_20261018.zip. Laptop, university PC and GitHub do not synchronize automatically.
