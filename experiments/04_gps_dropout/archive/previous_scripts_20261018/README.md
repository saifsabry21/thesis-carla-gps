# Experiment 05 — GPS output dropout

Status: prepared; not yet run or verified in CARLA.

## What this tests

The car remains parked. CARLA GNSS continues to generate measurements. A Python output gate withholds the reported coordinates during a five-second window. This emulates loss of GPS data availability at the software interface; it does not transmit interference, reproduce radio jamming, or change CARLA's raw sensor.

| Simulation time | Phase | Reported output |
|---|---|---|
| 0–5 s | Clean | Current GNSS coordinates |
| 5–10 s | Dropout | Unavailable; coordinate cells empty |
| 10–15 s | Recovery | Current GNSS coordinates restored |

No controller or VLA consumes this output yet, so no steering, collision, or end-to-end attack success is measured.

## Run on the university PC

Keep CARLA running in its original terminal. Put both Python files in `/home/g02-f26/thesis-gps`, then use a second terminal:

```bash
conda activate carla
cd /home/g02-f26/thesis-gps
python -u gps_dropout.py
```

The script first parks the car and positions the view. Press Enter in the terminal to start; immediately watch CARLA. Green status means output available; red means withheld. The green GPS marker disappears during dropout, while the ground-truth car remains visible. Capture the dropout phase or record the whole transition. The script waits again after recording, leaving the recovered car and labels visible. Press Enter when finished to remove this experiment's actors.

The CSV and metadata are saved before the final pause in a new `results/gps_dropout_TIMESTAMP/` folder. Do not expect exactly 50 samples per phase; boundaries depend on sensor timestamps.

Copy the actual results folder printed by the script into this command:

```bash
python check_gps_dropout.py results/gps_dropout_TIMESTAMP
```

The checker writes `validation.json` and reports whether all checks passed. Optional `--plot` creates PNG and SVG graphs if Matplotlib is installed; do not install packages just for this step, since plotting can be done on the laptop later.

## What the CSV means

- `frame`, `simulation_time`, `elapsed_seconds`: sample identity and simulation clock.
- `phase`: clean, dropout, or recovery.
- `output_available`: 1 when reported output is supplied, 0 when withheld.
- `sensor_x/y/z`: actual sensor position in the CARLA world.
- `clean_latitude/longitude/altitude`: original CARLA GNSS measurement, including during dropout.
- `reported_latitude/longitude/altitude`: current coordinates when available, empty during dropout. Empty does not mean a location of zero.

The raw log is for experiment verification; it is not a fallback input delivered through the attacked output gate. Recovery passes each current sample, without replaying the withheld readings. Because the vehicle is stationary, current and stale coordinate values may coincide; the static test alone cannot prove the difference from their numeric values.

## Evidence to archive after execution

Original CSV, metadata, checker report, CARLA screenshot or recording, graph, and actual observed phase/sample counts. Preparation checks do not establish an executed attack result.

## API reference

CARLA 0.9.14 GNSS sensor: https://carla.readthedocs.io/en/0.9.14/ref_sensors/#gnss-sensor

CARLA 0.9.14 Python API: https://carla.readthedocs.io/en/0.9.14/python_api/

## First execution and visual replay

The user reported a completed run `gps_dropout_20261018T114553_990157Z`: 50 clean, 50 dropout, and 50 recovery samples. The full CSV has not yet been independently checked or archived locally. The screenshot shows the completed recovery state; the user did not see the intended live status changes. The exact display/timing cause is not confirmed.

`replay_gps_dropout.py` is a separate presentation aid. It reads the original CSV and metadata, checks basic gate consistency, and displays each recorded phase until Enter is pressed. Its large colored point is an availability status light, not a GPS location. It creates a new parked illustration car at a free spawn point; this is not a reconstruction of the original vehicle's trajectory or a new attack trial. Original experiment files remain unchanged. The full checker is still needed to verify timing and sensor movement.

```bash
python check_gps_dropout.py results/gps_dropout_20261018T114553_990157Z
python -u replay_gps_dropout.py results/gps_dropout_20261018T114553_990157Z
```

The replay has passed local syntax checks; its CARLA visual appearance awaits the user's confirmation.

## Shapes replay (visual improvement)

The user supplied a checker report for `gps_dropout_20261018T114553_990157Z` with all 13 checks passing, 150 readings (50 per phase), 50 withheld outputs, and 0 m recorded sensor motion. Reported raw SHA256: CSV `40b0a2c55d36c709079e7cfcdd640061591e8f8731f35145e89903c00477da56`; metadata `750bb297b494aa369b3199476e7b298c85ccf4b6dd13728c3c95ba7bacd87084`. The report is user-supplied evidence; raw files still await local retrieval.

The first replay screenshots show correct phase labels, but its status points appear white. The exact rendering cause is not established. `replay_gps_dropout_shapes.py` replaces the point with line geometry: a green ring for clean/recovery, a red cross beside the car during dropout, and a blue vehicle outline throughout. This uses CARLA 0.9.14 DebugHelper.draw_line. Shapes encode output availability, not geographic error or a controller response. Phase snapshots wait for Enter, and no original data is modified. Syntax and geometric checks passed locally; actual colors and visibility must be checked in CARLA.

```bash
python -u replay_gps_dropout_shapes.py results/gps_dropout_20261018T114553_990157Z
```
