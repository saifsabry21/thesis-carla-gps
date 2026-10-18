# Start here after connecting to the university PC

These commands go into the **Ubuntu terminal on the university PC through RustDesk**. They do not go into Windows PowerShell on your laptop.

## 1. Connect and reach the Ubuntu desktop

The university PC must be powered on, connected to the network, and running RustDesk. If it is powered off, someone at university needs to switch it on. Connect using your existing RustDesk connection and log into the Ubuntu account if required.

## 2. Terminal 1: open CARLA

Open an Ubuntu terminal and run:

```bash
cd /home/g02-f26/carla_simulator/CARLA_0.9.14
./CarlaUE4.sh -windowed -ResX=1280 -ResY=720
```

Wait until the CARLA city appears. Keep this terminal open. It is busy running CARLA, so it will not show a normal command prompt while the simulator runs. If CARLA is already running, keep using the existing instance instead of launching another.

## 3. Terminal 2: activate Python

Open a second Ubuntu terminal or terminal tab. Run:

```bash
conda activate carla
cd /home/g02-f26/thesis-gps
python --version
```

The prompt should start with `(carla)`. The verified environment uses Python 3.8.20. Use this environment rather than `(base)`.

If this fresh terminal says that `conda` is not found, initialize the existing installation, then activate it:

```bash
source /home/g02-f26/miniconda3/etc/profile.d/conda.sh
conda activate carla
cd /home/g02-f26/thesis-gps
```

If the `thesis-gps` directory is missing, stop and check the signed-in account and installation before creating a replacement.

## 4. Check the CARLA connection

Copy the complete block, including its final `PY` line:

```bash
python - <<'PY'
import carla

client = carla.Client("localhost", 2000)
client.set_timeout(20.0)
print("Client:", client.get_client_version())
print("Server:", client.get_server_version())
print("Map:", client.get_world().get_map().name)
print("Connection successful")
PY
```

Expected versions: client 0.9.14 and server 0.9.14. The previously used map is `Carla/Maps/Town10HD_Opt`. If the connection times out, first check that CARLA has finished loading in Terminal 1. If the versions or map differ, keep the output so we can review the changed setup before comparing new results.

`check_connection.py` in this setup folder contains the reusable check. The inline block works even if that helper has not been transferred to Ubuntu.

## 5. Transfer the experiment files you need

Use RustDesk File Transfer. On your laptop, open the selected folder under `Thesis 1 work/experiments/`. On the university side, open `/home/g02-f26/thesis-gps/`. Copy the required Python files into that university directory.

Each attack now has one self-contained script:

- Fixed offset: `experiments/02_gps_fixed_offset/gps_fixed_offset.py`
- Gradual drift: `experiments/03_gps_gradual_drift/gps_gradual_drift.py`
- Dropout: `experiments/04_gps_dropout/gps_dropout.py`

The two latest offset/drift versions are packaged together in `setup/updates/gps-unified-updates.zip`. Transfer this ZIP to Ubuntu `~/thesis-gps` and extract it with `python -m zipfile -e gps-unified-updates.zip .`. It replaces the two named scripts. New offset/drift versions passed local checks but have now been run successfully in real CARLA; their latest versions have been transferred and executed successfully. The combined dropout version was run successfully by the user.

## 6. Choose one experiment to run

Run one of these commands in Terminal 2 after activating `carla` and entering `~/thesis-gps`:

| Experiment | Command |
|---|---|
| Clean baseline | `python gps_baseline.py` |
| Fixed five-metre offset | `python -u gps_fixed_offset.py` |
| GPS dropout | `python -u gps_dropout.py` |
| Gradual drift: verified experiment | `python -u gps_gradual_drift.py` |

The baseline writes `gps_baseline.csv` into the terminal's current directory and overwrites a file with that name. The original completed baseline is safely archived on the laptop under `experiments/01_gps_baseline/results/recorded_baseline/`. Preserve any new unarchived baseline CSV before rerunning.

The offset and drift scripts create new timestamped folders under the script's `results/` directory, so separate runs do not overwrite one another.

## 7. Use the visuals and finish the run

For the current combined attack scripts:

1. At the initial prompt, inspect the car, then press Enter in Terminal 2 to start.
2. Look at the CARLA window while the experiment runs.
3. After automatic validation, a clearly labeled recorded review pauses at each phase for screenshots.
4. Press Enter in Terminal 2 when finished viewing so the script removes its test car and sensor and finalizes its output.

The green marker identifies the real position. The red marker identifies the false reported GPS position. The arrow illustrates their difference. It does not show the car driving.

The city view alone is not evidence that the test car is still present: the script removes its car after the final Enter. If a visual is unclear, capture the scene while the final viewing prompt is still active.

## 8. Save and share evidence

Transfer the completed timestamped run folder from Ubuntu `~/thesis-gps/results/` into the matching laptop experiment's `results/` folder. Keep the original `readings.csv` and `metadata.json` unchanged. Keep screenshots and analysis beside the run they document.

Checks now run automatically. To check an existing drift run without starting CARLA:

```text
python gps_gradual_drift.py --check results/<exact drift run folder printed by the script>
```

Replace the angle-bracket placeholder with the real folder name. Do not paste it literally. The checker runs without CARLA or extra Python packages. Graph generation is optional and needs Matplotlib; see the drift experiment's README.

Archive verified results in GitHub and prepare a short progress-table entry. Editing the team's Google Doc is a separate step.

## Quick troubleshooting

| Symptom | First check |
|---|---|
| RustDesk says offline | University PC power, network, and RustDesk availability |
| Terminal cannot accept commands while CARLA runs | Open Terminal 2; Terminal 1 is occupied by CARLA |
| `No module named carla` | Activate `conda activate carla` in that terminal |
| Script file not found | Check you are in `~/thesis-gps` and transferred the selected script |
| Connection timeout | Confirm CARLA is open and has finished loading |
| `bind: Address already in use` followed by a crash | Check for an existing CARLA process or a process using port 2000; see the restart steps below |
| Synchronous-world warning | Send the output for review rather than changing the shared world settings |

The university setup and laptop folder structure are separate. These instructions preserve the university paths already used successfully. No software installation or power-setting changes are required by this guide.

## If startup reports `bind: Address already in use`

This was observed and resolved on 18 October 2026. A previous CARLA process was still running. The user stopped it, then relaunched successfully. The error text alone does not prove every future conflict is CARLA, so identify the process before stopping anything.

If the original CARLA terminal is available, press Ctrl+C there to stop that instance. Otherwise, inspect:

```bash
pgrep -af '[C]arlaUE4-Linux-Shipping'
ss -ltnp 'sport = :2000'
```

The first number on a process line is its PID. Stop only the identified CARLA instance with `kill -TERM` followed by its actual PID. For example, if and only if its PID were 12345:

```bash
kill -TERM 12345
```

Check again with `pgrep`. If multiple processes appear or the port belongs to a different application, review the output before terminating anything else. After the selected instance exits, launch CARLA using the Terminal 1 commands above.


All three combined scripts have now been transferred and executed; checks passed. Use the current experiment README for the latest run.

## Current simplified evidence layout

On the laptop, each experiment has one flat results/ folder. To check it from its experiment folder use `python SCRIPT.py --check results`; to replay use `python -u SCRIPT.py --replay results`. Replace SCRIPT.py with that experiment's single active script. University runs still have timestamped folders. Older laptop runs are now archived.
