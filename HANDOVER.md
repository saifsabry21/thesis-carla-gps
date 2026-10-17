# Handover for the next working session

Session documented: 18 October 2026, Cairo.

## Completed

- CARLA 0.9.14 and the matching Python client connect successfully on Town10HD_Opt.
- Clean parked-car baseline: 100 readings archived.
- Fixed GPS-output offset: 101 readings, 50 clean and 51 attacked. Approximately 5 m displacement verified.
- Visual version: another 101-reading run with the same manipulation, plus real/false-position labels and a five-metre arrow. Screenshot archived.
- Both offset runs passed all 13 archived-data checks. Their raw files are kept in separate timestamped folders.
- Code, raw evidence, graphs, and notes are saved locally and archived in the private GitHub repository.
- The shared Google Doc remains unchanged. Each offset run has a draft progress-table entry in its experiment notes.

## Keep these scripts

| Script | Role |
|---|---|
| `gps_baseline.py` | Original no-attack reference; rerunning overwrites its CSV in the current directory |
| `gps_fixed_offset.py` | Simpler measurement experiment; saves each run separately |
| `gps_offset_visual.py` | Same manipulation with CARLA markers and pauses; saves each run separately |
| `analyze_gps_offset.py` | Rechecks and plots saved CSV data locally; needs Matplotlib, not CARLA |

## Important scope

The scripts modify the GPS output reported by our Python program. They do not alter CARLA's underlying sensor measurements or move the car. No driving controller or VLA consumes the false output yet. No driving effect, safety violation, or end-to-end ASR has been evaluated. The markers explain a position error, not a vehicle trajectory. The current visual has a strong red glow that partially obscures the car; appearance improvements are pending.

## Restart at the university PC

If CARLA is no longer running, start it in its own terminal:

```bash
cd /home/g02-f26/carla_simulator/CARLA_0.9.14
./CarlaUE4.sh -windowed -ResX=1280 -ResY=720
```

In a separate terminal:

```bash
conda activate carla
cd ~/thesis-gps
python -u gps_offset_visual.py
```

Press Enter at the first prompt to start recording. At the last prompt, view or capture the scene before pressing Enter to remove the test objects and finalize metadata.

## Next technical work

1. Improve marker clarity for presentation if needed, preserving the existing executed scripts as archived versions.
2. Inspect the team's current driving/model integration and identify exactly which component consumes GPS. Do not assume CARLA autopilot or Alpamayo consumes this sensor output.
3. Once that input path is confirmed, connect the manipulation there and establish a moving clean baseline before comparing matched clean and attacked driving runs.

Additional attack types and repeated-trial evaluation remain future work. Do not report today's two runs as an end-to-end success percentage.

## Practical notes

The laptop folder, private GitHub repository, and Ubuntu folder do not automatically synchronize. Transfer new run folders after the script completes. Preserve raw data and settings, then update the corresponding notes. Keep the university PC powered and connected if remote access is needed; this session did not change power or sleep settings.
