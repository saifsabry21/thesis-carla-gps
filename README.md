# Thesis CARLA GPS experiments

Start with [setup/START_HERE.md](setup/START_HERE.md). Each attack has one active script containing the attack, live visuals, automatic checks, chart, summary and recorded review.

| Experiment | Active script | Latest documented result |
|---|---|---|
| [Baseline](experiments/01_gps_baseline/README.md) | gps_baseline.py | 100 original readings archived |
| [Fixed offset](experiments/02_gps_fixed_offset/README.md) | gps_fixed_offset.py | +5 m; 51 clean / 49 attack; 14 checks passed |
| [Gradual drift](experiments/03_gps_gradual_drift/README.md) | gps_gradual_drift.py | 0→10 m; 51 clean / 100 drift / 49 hold; 14 checks passed |
| [Dropout](experiments/04_gps_dropout/README.md) | gps_dropout.py | 50 clean / 50 withheld / 50 recovery; 13 checks passed |

The latest combined runs are documented in each experiment's timestamped results folder. Original downloaded CSVs, metadata, server-generated reports, charts and summaries are retained. Local validation reports independently check the downloaded files and confirm matching script hashes. Additional downloaded runs are preserved without being counted as additional verified presentation trials.

Screenshots are stored beside their corresponding run. Fixed-offset screenshots are recorded review; the drift set includes a live approximately 6 m image plus review images. Colored dropout screenshots replay the earlier 11:45 UTC recording; the later combined run has its own data and report. Replays are visual explanations, not new attacks.

The physical vehicle remained parked. These experiments manipulate the Python-reported GPS output; they do not transmit RF interference or establish controller/VLA attack success. The next stage is to connect attacked output to a consumer and evaluate its response.

Old scripts and earlier visual fixed-offset evidence remain in experiment archives. Setup transfer ZIPs contain copies of the active scripts for convenience. The full inbound result snapshot is in archive/backups/university_results_20261018.zip. Laptop, university PC and GitHub do not synchronize automatically.
