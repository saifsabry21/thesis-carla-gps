# Gradual GPS drift — one script

Use **gps_gradual_drift.py**. It contains the live attack, visuals, CSV and metadata saving, automatic validation, SVG chart, summary, and recorded review. No archived helper scripts or plotting packages are required.

## Run on Ubuntu

Keep CARLA running; use a second terminal:

```bash
conda activate carla
cd ~/thesis-gps
python -u gps_gradual_drift.py
```

The car remains parked. Press Enter to start. The recording runs continuously: 5 clean + 10 drift + 5 hold simulation seconds; 0 to +10 m at 1 m/s in CARLA map X. Original CARLA GNSS measurements are preserved, while reported coordinates are modified. Green marks the real position; red marks the reported position. The arrow shows position error, not a trajectory or driving response. Map X is not necessarily geographic east or the car's forward direction.

After recording, the script checks the CSV and metadata, then saves `validation.json`, `gps_offset_plot.svg`, and `RESULT_SUMMARY.md` beside the raw results. A new timestamped folder is used for every run. Existing `validation.json` files are preserved; a later check writes `validation_unified.json`.

The automatic recorded review pauses at each phase for screenshots. Drift review animates the actual recorded offsets before pausing. Review imagery is explicitly labeled as replay. It uses a parked illustration vehicle at an available spawn point, not a reconstruction of the original vehicle trajectory. Press Enter to advance and finally remove the car.

## Replay the existing recording

```bash
python -u gps_gradual_drift.py --replay results/gps_gradual_drift_20261018T111345_116556Z
```

## Check without CARLA

```bash
python gps_gradual_drift.py --check results/gps_gradual_drift_20261018T111345_116556Z
```

## Verification and scope

The new version passed Python 3.8 syntax checks, read-only validation against the archived real run, and temporary synthetic checks of recording, validation, cleanup, SVG writing, and rejection of corrupted coordinates. Its combined-script CARLA run `gps_gradual_drift_20261018T124241_669723Z` has now completed, with all 14 checks passing remotely and locally. Synthetic test data was removed and is not experiment evidence.

This is GPS-output manipulation in software. No radio signal is transmitted and no driving controller or VLA consumes the attacked output. Validation does not establish driving attack success.

Only `gps_gradual_drift.py` is active. Previous sources and the guide are preserved byte-for-byte with hashes in `archive/previous_scripts_20261018/`. Original results remain unchanged.

API documentation: https://carla.readthedocs.io/en/0.9.14/python_api/


Latest verified combined run: `gps_gradual_drift_20261018T124241_669723Z`. All three consolidated scripts have now completed their university CARLA runs; see the root README for exact results.
