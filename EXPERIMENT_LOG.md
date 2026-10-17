# Experiment log

## Session: 2026-10-17

Owner: Saif. Execution machine: university Ubuntu PC, accessed through RustDesk.

### Completed milestones

| ID | Task | Observed result | Status |
|---|---|---|---|
| SETUP-01 | Inspect machine and installation | Ubuntu 24.04.3; RTX 3090; CARLA installation located | Verified |
| SETUP-02 | Start CARLA | Town rendered successfully | Verified |
| SETUP-03 | Activate existing Python environment | Python 3.8.20; CARLA import successful | Verified |
| CONN-01 | Connect Python client to server | Client and server 0.9.14; Town10HD_Opt | Verified |
| GNSS-BASE-01 | Spawn parked vehicle and attach GNSS | 100 readings reported; CSV saved | Verified |
| VIS-01 | Inspect vehicle in CARLA | Car visible after waiting before reading its location and repositioning spectator | Verified |
| DATA-01 | Archive saved baseline CSV | Original full CSV copied from university PC; 100 measurement rows; first five match the chat excerpt | Verified and archived |
| DATA-02 | Archive executed source | Original `gps_baseline.py` copied from university PC through RustDesk | Archived without source changes |
| GPS-OFFSET-01 | Fixed +5 m GNSS-output offset | 50 clean and 51 attacked readings; approximate 5 m separation verified | Verified at output level; driving not tested |

### What changed during troubleshooting

- CARLA's initial spectator view did not follow the spawned vehicle automatically.
- A top-down spectator position was added.
- The script was changed to wait for Enter after recording, preventing immediate cleanup during inspection.
- A process check at one point showed no running baseline process and no Tesla actor; the exact reason it exited was not established.
- A two-second wait before querying the spawned vehicle's position was then added. The next run showed the test car correctly.
- The successful visual run reported vehicle ID 30 at x=-64.644844, y=24.471010, z=0.001788. IDs and spawn results should not be assumed identical in future runs.

### Team-table entry

| Sensor | Type of attack | Outcome on CARLA | Success? | Completed by | Code found in | Sources |
|---|---|---|---|---|---|---|
| GPS/GNSS | No attack: clean stationary baseline | Vehicle and sensor spawned; 100 readings reported; CSV saved; car visually inspected | Baseline verified; attack success not applicable | Saif | `gps_baseline.py` | Official CARLA GNSS documentation |

### Interpretation

This proves that the sensor can be attached, read, and logged in the existing CARLA setup. It does not prove an attack, vehicle robustness, or an effect on a VLA.

### Next work, not completed results

1. Preserve the archived original CSV before any rerun overwrites it.
2. Completed subsequently: fixed GPS offset with clean and modified values archived; see the run below.
3. Identify the component that consumes GPS; built-in driving behavior must not be assumed to use the GNSS sensor.
4. Establish a moving baseline and matched clean/attacked scenarios.
5. Define repeated-trial measurements and only then evaluate driving effects.

## GPS-OFFSET-01: recorded 2026-10-17 21:18:19 UTC

One parked-car run completed with 101 readings (50 clean, 51 attacked). All 13 archived-data checks passed. The first affected sample occurred at 5.001833 simulated seconds. Original sensor positions remained constant; reported GPS differed by approximately five metres during the attack.

[Full experiment notes, evidence, and team-document draft](results/gps_fixed_offset_20261017T211819_023749Z/EXPERIMENT_NOTES.md). No driving controller or VLA was tested, and no end-to-end ASR is claimed.

## GPS-VISUAL-01: visual run recorded 2026-10-17 21:46:33 UTC

Same manipulation plus on-screen position markers and pauses. 101 readings (50 clean, 51 attacked), all 13 data checks passed. The screenshot supplied by Saif is preserved with this run. Source CSV and metadata were transferred from the university PC. [Run notes and evidence](results/gps_offset_visual_20261017T214633_130642Z/EXPERIMENT_NOTES.md). Driving/VLA effects remain untested.
