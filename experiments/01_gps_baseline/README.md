# 01 - Clean GPS baseline

**Status: completed and verified. No attack.**

The original script spawns a parked Tesla Model 3, attaches a GNSS sensor, records clean readings, and saves a CSV. The archived run contains 100 readings. These establish that CARLA's sensor can be attached, read, and logged.

## Files

- `gps_baseline.py`: original executed source, unchanged.
- [results/recorded_baseline/](results/recorded_baseline/): original full CSV, five-row excerpt, and transcribed terminal excerpts.

## Run on the university PC

Follow [the setup guide](../../setup/START_HERE.md), then run in Terminal 2:

```bash
conda activate carla
cd ~/thesis-gps
python gps_baseline.py
```

The script records for ten wall-clock seconds, then waits for Enter before removing the car and writing the CSV. Its output is relative to the terminal's current directory, unlike the later scripts which save beside their source. Preserve any unarchived `gps_baseline.csv` before rerunning.

The archived original CSV is protected in this experiment's `results/recorded_baseline/` folder. A new local run started from this experiment folder would write a new CSV next to the script, not into that archive. CARLA execution still takes place on the university PC.

No moving-vehicle or VLA result is established by this baseline.
