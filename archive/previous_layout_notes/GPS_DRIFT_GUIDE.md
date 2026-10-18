# Gradual GPS drift: ready to execute

Status: prepared locally. Syntax and attack-profile boundary checks have passed. This experiment has not yet been executed in CARLA. No results, screenshot, counts, or success rate are claimed.

## Goal

Gradually move the reported GPS position away from the original measurement while the actual vehicle remains parked. This changes our Python program's reported output; no controller or VLA is connected. It is a software emulation, not a radio-frequency spoofing experiment.

## Planned sequence

| Simulation elapsed time | Phase | Reported position offset along map X |
|---|---|---|
| 0 to less than 5 seconds | Clean | 0 m |
| 5 to less than 15 seconds | Drift | Increases from 0 towards 10 m at 1 m/s |
| 15 to less than 20 seconds | Hold | 10 m |

The increasing offset does not mean the car moves at 1 m/s. Only its false reported position moves. There is no sudden five-metre step as in the earlier test. The 20-second duration uses GNSS simulation timestamps, not wall-clock timing. Sample counts depend on the delivered measurements and should not be assumed in advance.

## Files to transfer

Through RustDesk File Transfer, copy `gps_gradual_drift.py` and `check_gps_drift.py` from your laptop repository folder into `/home/g02-f26/thesis-gps/`. Keep all existing scripts.

## Start

With CARLA running, use a separate university Ubuntu terminal:

```bash
conda activate carla
cd ~/thesis-gps
python -u gps_gradual_drift.py
```

1. The script spawns a parked vehicle and moves the spectator above it.
2. At the first prompt, inspect the car, then press Enter in the terminal to start.
3. Switch to the CARLA window. The green marker shows the real position. The red reported-position marker should move away during the drift phase, then stop at ten metres.
4. The terminal prints the phase and applied offset roughly once per simulation second.
5. After recording, the car and final markers remain visible. Take a screenshot. A screen recording is preferable for showing the gradual change; a still screenshot only shows the final displacement.
6. Press Enter in the terminal when finished viewing. The script removes its test objects.

The arrow is a visual explanation of the position error, not a path driven by the vehicle. Marker heights are adjusted for visibility and do not represent altered GPS altitude. This version uses a thinner arrow and shorter-lived marks to reduce overlapping glow; appearance must still be checked in the actual simulator.

## Saved evidence

Each run creates `results/gps_gradual_drift_<UTC timestamp>/` beside the script. It contains `readings.csv` and `metadata.json`. Settings and sample counts are saved after recording, before the final viewing pause, and updated during cleanup.

The CSV includes the frame, simulation timestamp, elapsed time, phase, applied map-X offset, true sensor XYZ, and original/reported latitude, longitude, and altitude. Keep these original files unchanged.

## Verify the actual results

Replace the example folder below with the exact path printed by your run:

```bash
python check_gps_drift.py results/gps_gradual_drift_<actual timestamp>
```

The checker uses only Python's standard library and saves `validation.json`. It checks phase timing, the offset profile, approximate geographic separation, counts, and whether the recorded sensor position stayed stationary. The geographic distance check uses a spherical approximation appropriate to this initial check on the current CARLA map.

To generate a graph later on a computer with Matplotlib:

```bash
python check_gps_drift.py results/gps_gradual_drift_<actual timestamp> --plot
```

This produces `gps_drift_plot.png` and `gps_drift_plot.svg` from actual readings. The earlier `analyze_gps_offset.py` checks a fixed offset and is not the appropriate checker for this drift profile.

## After the test

Send the terminal output and a CARLA screenshot. Transfer the full completed run folder to the laptop's repository `results/` folder. Then verify the measurements, make the graph, document the observed outcome, and archive the verified evidence in GitHub. Update the shared progress document only when requested.

For the team meeting, distinguish successful GPS-output manipulation from a demonstrated driving or VLA effect. The latter remains untested until a driving component receives the manipulated output.

## References

- [CARLA 0.9.14 GNSS sensor](https://carla.readthedocs.io/en/0.9.14/ref_sensors/#gnss-sensor)
- [CARLA Python API, including map conversion and DebugHelper](https://carla.readthedocs.io/en/0.9.14/python_api/)
- [Shen et al. (2020), Drift with Devil](https://www.usenix.org/conference/usenixsecurity20/presentation/shen): related GPS-spoofing research against localization fusion. This simple experiment does not reproduce FusionRipper's full algorithm or evaluation.
