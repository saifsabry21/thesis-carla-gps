# Current progress and next work

Updated 18 October 2026, Cairo.

## Completed

- University CARLA client and server 0.9.14 connect successfully on Town10HD_Opt.
- Clean baseline: 100 readings archived in [experiment 01](../experiments/01_gps_baseline/README.md).
- Fixed position offset: 50 clean and 51 attacked readings. All 13 archived-data checks passed. See [experiment 02](../experiments/02_gps_fixed_offset/README.md).
- Visual fixed offset: a separate 50-clean/51-attacked run, with all 13 checks passed and a screenshot preserved. See [experiment 03](../experiments/03_gps_fixed_offset_visual/README.md).
- The organized folders, scripts, startup guides, raw evidence, and completed drift-run notes are archived in the private GitHub repository.

## Gradual drift: now completed

[Experiment 04](../experiments/04_gps_gradual_drift/README.md) was transferred to Ubuntu and executed. It recorded 200 readings (51 clean, 99 drift, 50 hold). All 12 checks passed remotely and locally. The original files, screenshot, graph, and notes are archived in its results folder. Driving/VLA effects remain untested.

[Completed run](../experiments/04_gps_gradual_drift/results/gps_gradual_drift_20261018T111345_116556Z/EXPERIMENT_NOTES.md).

## Next session

1. Follow [the startup guide](../setup/START_HERE.md).
2. Review the verified drift result and the draft progress-table entry.
3. If a second new sensor-output test is needed, implement GPS dropout as a separate experiment.
4. Identify the driving-system component that will consume manipulated GPS before claiming a driving effect.

GPS dropout remains a possible later experiment; no dropout implementation or result is claimed. The shared Google Doc has not been edited.

## Scope

The scripts manipulate GPS output inside our Python program. No false GPS input has reached a controller or VLA yet. No driving safety outcome or end-to-end ASR has been established. Reading counts are not independent attack-trial counts.

## Folder cleanup

The laptop files now live directly under `Thesis 1 work`, grouped into setup, experiments, project notes, and archive. The original scripts and recorded data are preserved byte-for-byte. Earlier global notes and the existing ZIP are retained under `archive/`.

The private GitHub repository now matches the organized laptop layout. The university execution folder remains `~/thesis-gps/`; this update does not move files on that PC. The preserved ZIP contains the earlier completed session and predates the drift files and results.

## Startup issue resolved today

CARLA startup failed with `bind: Address already in use`, followed by a segmentation fault. The user stopped the previous CARLA process and successfully launched a fresh instance. See the setup guide for identifying that specific process and restarting. No GPU driver, Ubuntu, or CARLA installation change was needed for this observed incident.
