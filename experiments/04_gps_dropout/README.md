# GPS dropout — one script

Use **gps_dropout.py** for this experiment. It contains the attack, ring/cross visuals, validation, chart generation, results summary, and saved-result replay. It does not import any of the archived scripts.

## Run a new experiment

Keep CARLA running. In a second terminal:

```bash
conda activate carla
cd ~/thesis-gps
python -u gps_dropout.py
```

1. A parked car appears with a blue outline. Press Enter to begin recording.
2. The script records 5 clean + 5 dropout + 5 recovery **simulation seconds**. The live view uses a green ring when output is available, and a red cross with no ring during dropout.
3. It saves original and reported readings, settings, and the script hash in a new timestamped results folder.
4. It automatically checks the saved CSV and metadata. Validation failure stops the review and retains data for diagnosis.
5. It creates `validation.json`, `gps_dropout_plot.svg` (opens in a browser), and `RESULT_SUMMARY.md`. No plotting library is needed.
6. It then shows a **recorded replay**, pausing at each phase for screenshots. Press Enter to advance; the final Enter removes the car.

The default live recording does not pause between phases, so its timing remains continuous. The later screenshot pauses are a replay of the recorded phases, not new attack measurements. They are clearly labeled in CARLA. Each replay uses an illustration car at an available spawn point; it is not a reconstruction of an earlier vehicle trajectory.

## Show the already verified run without repeating the attack

```bash
python -u gps_dropout.py --replay results/gps_dropout_20261018T114553_990157Z
```

This validates the stored results, saves the chart and summary, then shows the three phases. An existing `validation.json` is preserved; a new check report is written as `validation_unified.json`.

## Check results without opening CARLA

```bash
python gps_dropout.py --check results/gps_dropout_20261018T114553_990157Z
```

## What was measured

The output gate withholds reported latitude, longitude, and altitude during dropout, leaving their CSV cells empty. `output_available` is 0 during dropout and 1 otherwise. Raw CARLA GNSS values continue to be logged for verification. Recovery passes the current sample. Original raw coordinates and the vehicle are not manipulated. A parked experiment cannot independently prove fresh versus stale equal-valued coordinates from the coordinate values alone.

This is a software simulation of missing GPS output, not radio jamming. No driving controller or VLA consumes the attacked output, so collision or driving attack success is not measured.

## Existing result

The user supplied a completed checker report for `gps_dropout_20261018T114553_990157Z`: all 13 checks passed; 150 samples (50 per phase); 50 withheld outputs; maximum recorded sensor motion 0 m. The ring/cross replay was subsequently confirmed by screenshots. The raw result files have now been downloaded to this folder and verified locally.

That run was produced by the older attack script, preserved in `archive/previous_scripts_20261018/`. The consolidated version has passed Python 3.8 syntax checks and a temporary synthetic integration test of recording, validation, chart writing, single-stop cleanup, and rejection of corrupted output. Its combined-script CARLA run `gps_dropout_20261018T122858_646455Z` has now completed, with all 13 checks passing remotely and locally. Synthetic fixtures are not experiment evidence and were removed after testing.

## Folder layout

- `gps_dropout.py`: the only active Python script.
- `README.md`: this guide.
- `results/`: actual recorded runs, once copied from the university machine.
- `archive/previous_scripts_20261018/`: historical sources and previous guide, with original hashes. Not needed to run the current script.

## One-time cleanup on the university PC

After the new `gps_dropout.py` has been transferred, the old helper scripts can be moved out of the working folder:

```bash
mkdir -p archive/gps_dropout_previous_scripts
for file in check_gps_dropout.py replay_gps_dropout.py replay_gps_dropout_shapes.py; do
    if [ -f "$file" ]; then mv -n -- "$file" archive/gps_dropout_previous_scripts/; fi
done
```

The original attack source is already preserved in the laptop archive. Other experiments and recorded results remain in place.

## Documentation

CARLA 0.9.14 Python API: https://carla.readthedocs.io/en/0.9.14/python_api/

GNSS sensor: https://carla.readthedocs.io/en/0.9.14/ref_sensors/#gnss-sensor


Latest verified combined run: `gps_dropout_20261018T122858_646455Z`. All three consolidated scripts have now completed their university CARLA runs; see the root README for exact results.
