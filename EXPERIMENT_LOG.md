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
| GPS-OFFSET-01 | Implement and evaluate GPS offset | Code proposed in chat; no execution evidence | Not performed |

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
2. Validate a fixed GPS position offset and log clean versus modified values.
3. Identify the component that consumes GPS; built-in driving behavior must not be assumed to use the GNSS sensor.
4. Establish a moving baseline and matched clean/attacked scenarios.
5. Define repeated-trial measurements and only then evaluate driving effects.
