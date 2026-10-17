# Thesis CARLA GPS Experiments

Saif's scripts and evidence for the GPS/GNSS part of the team's autonomous-driving thesis.

## Current milestone

**A clean, stationary GNSS baseline has been verified. No GPS attack has been run or evaluated yet.**

On the university Ubuntu PC, we launched CARLA 0.9.14, connected using its Python API, spawned a parked Tesla Model 3, attached a GNSS sensor, and collected 100 measurements. The car was also confirmed visually in the simulator. The experiment saves readings to CSV and removes its own test vehicle and sensor.

This is preparation for later single-sensor experiments. It does not demonstrate GPS effects on driving, a GPS-consuming controller, or Alpamayo integration.

## Files

| File | Purpose and provenance |
|---|---|
| `gps_baseline.py` | Original executed baseline script downloaded directly from `/home/g02-f26/thesis-gps/` through RustDesk file transfer. |
| `check_connection.py` | Previously successful connection-check commands saved as a reusable script. |
| `launch_carla.sh` | Previously successful university-PC launch commands saved as a shell script. |
| `inspect_system.sh` | Earlier read-only machine and setup checks saved as a reusable command list. |
| `inspect_vehicle.py` | Earlier camera/vehicle diagnostic saved as a reusable script; selects a Tesla only when exactly one exists. |
| `vehicle_inspection_output.txt` | Actual earlier diagnostic result when no Tesla was present; clearly separated from the later successful run. |
| `gps_baseline.csv` | Original full dataset downloaded from the university PC: header plus 100 measurement rows. |
| `gps_baseline_excerpt.csv` | The five rows previously pasted in chat, retained as a quick preview; they match the start of the full file. |
| `connection_output.txt` | Actual connection output supplied in chat. |
| `baseline_output.txt` | Clearly labeled actual terminal excerpts from separate baseline observations. |
| `environment.txt` | Recorded machine and software details. |
| `EXPERIMENT_LOG.md` | Milestones, explanations, limitations, and meeting notes. |
| `DATA_PROVENANCE.md` | Original file locations, integrity hashes, and checks on the downloaded data. |

The original script and full CSV were copied from the university PC without rerunning or modifying the experiment. All 100 measurement rows are included; no measurements were generated to fill gaps. The CSV starts at simulation time 884.1190541145043 and ends at 894.0189892392955. A rerun overwrites the CSV in the working directory, so preserve the archived dataset before running the experiment again there.

## Run on the university Ubuntu PC

These instructions assume the existing installation and `carla` Conda environment. They do not install or change dependencies.

In terminal 1:

```bash
bash launch_carla.sh
```

Keep that terminal open. In terminal 2, activate the environment and switch to the folder containing these scripts:

```bash
conda activate carla
cd /path/to/this/repository
python check_connection.py
python gps_baseline.py
```

The baseline script waits for the vehicle position to settle, moves the viewing camera above the vehicle, and records for 10 real-world seconds. After recording it waits for Enter so the car can be inspected. Press Enter to clean up and save `gps_baseline.csv` in the current working directory. This file is overwritten on a later run in the same directory.

The launch script has the verified university installation path. If used elsewhere, edit that path first.

## Understand the baseline

1. Connect to the existing CARLA server on `localhost:2000`.
2. Find an available map spawn point and create a Tesla Model 3.
3. Apply the brake and handbrake; no autonomous controller is enabled.
4. Wait two seconds before reading the vehicle position and placing the spectator camera.
5. Attach `sensor.other.gnss` 1.5 m above the vehicle attachment origin.
6. Request one GNSS measurement every 0.1 simulated seconds.
7. Store frame number, simulation timestamp, latitude, longitude, and altitude in memory.
8. After 10 real-world seconds, stop the sensor and wait for visual inspection.
9. Remove the test objects and save the readings.

The spectator is only the viewing camera. Moving it does not move the car or alter GPS. The altitude is the GNSS sensor altitude, not a direct road-height measurement.

## CSV columns

| Column | Meaning |
|---|---|
| `frame` | Simulation frame associated with the measurement |
| `simulation_time` | CARLA timestamp in simulated seconds |
| `latitude` | Reported latitude in degrees |
| `longitude` | Reported longitude in degrees |
| `altitude` | Reported GNSS altitude in meters |

Unchanged latitude and longitude are expected for the parked car. They are simulated map coordinates, not the university's real GPS location.

## Meeting summary

> I verified the CARLA installation and its Python connection, then implemented a stationary GNSS baseline. The script spawns a vehicle, attaches a GNSS sensor, records timestamped readings, and saves them to CSV. We collected 100 readings and confirmed the car visually. Next we will validate a controlled GPS offset, then establish how GPS enters the driving controller before measuring effects on driving.

## Limits of these results

- The 100-reading count is an observed run result, not a guaranteed count on every machine.
- The recording duration uses wall-clock time; a fixed-step synchronized experiment has not been configured.
- No route, moving-vehicle baseline, repeated-trial statistics, or attack success rate has been established.
- No GPS-consuming driving controller or GPS-to-Alpamayo input path has been verified.
- The proposed GPS-offset script was not included as completed work because execution was paused to document the baseline.

## Official implementation references

- [CARLA 0.9.14 GNSS sensor](https://carla.readthedocs.io/en/0.9.14/ref_sensors/#gnss-sensor)
- [CARLA 0.9.14 Python API](https://carla.readthedocs.io/en/0.9.14/python_api/)
- [CARLA simulation timing](https://carla.readthedocs.io/en/0.9.14/adv_synchrony_timestep/)
