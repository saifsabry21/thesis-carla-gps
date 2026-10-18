# Data provenance

The following two files were copied from the university Ubuntu PC using the existing RustDesk file-transfer session. The experiment was not rerun to create these copies.

| File | Original location | SHA-256 |
|---|---|---|
| gps_baseline.py | /home/g02-f26/thesis-gps/gps_baseline.py | 196322198d91951eb8bcd86b98cfa79c489f19cf41ffcc58cc1c9f0833579359 |
| gps_baseline.csv | /home/g02-f26/thesis-gps/gps_baseline.csv | 72f524fcc525d4311333d26dfd3a2b0012e595ed096b1ee1eebde92c32d5b483 |

## Checks

- Full CSV: 100 data rows plus a header.
- The five-row chat excerpt exactly matches the first five full-CSV rows.
- Python syntax parsed successfully for both Python files; no local CARLA execution was attempted.
- First simulation timestamp: 884.1190541145043.
- Last simulation timestamp: 894.0189892392955.
- Covered simulation interval: 9.899935124791227 seconds between the first and last samples.
- Latitude, longitude, and altitude are constant throughout this stationary dataset.
- No GPS attacks or VLA-driving results are claimed.

Connection output, machine details, and other console excerpts were transcribed from user-provided terminal output and are labeled separately from the original downloaded files.

## Fixed GPS-output offset run

Original readings and metadata were downloaded through RustDesk File Transfer from `/home/g02-f26/thesis-gps/results/gps_fixed_offset_20261017T211819_023749Z/`. The full original files are preserved in `results/gps_fixed_offset_20261017T211819_023749Z/`. The CSV has 101 measurements: 50 clean and 51 attacked.

- `readings.csv`: SHA-256 `1117dd39783399ad73d2282baf4a32d6f45f41b6cde5abb7524112c462a1f385`.
- `metadata.json`: SHA-256 `ddacd7ff40c2a02a9fcb950ac9089542644f2366a711410fe53e0de275a2d5f0`.

`gps_fixed_offset.py` is the supplied source executed by the user on the university PC. `analyze_gps_offset.py` was executed locally after transfer. Its validation file, plots, and experiment notes are derived artifacts, not raw CARLA outputs. No synthetic rows were added.

## Visual fixed-offset run

Original CSV and metadata were downloaded through RustDesk from `/home/g02-f26/thesis-gps/results/gps_offset_visual_20261017T214633_130642Z/` and preserved in `results/gps_offset_visual_20261017T214633_130642Z/`. The user-supplied CARLA screenshot is archived unedited; no exact sensor-frame association is claimed. Plots, validation, and notes are locally derived from this visual run.

- `readings.csv`: SHA-256 `f4a52051dc11bfd4db98bb9c9a0600f9916a04a4aa403ba0642c676cc3b96585`.
- `metadata.json`: SHA-256 `009997f20cb1727e117fba11adae09c29ecd3fc9dfb58ce36be7cd8ed014dad8`.
- `carla_visual_screenshot.png`: SHA-256 `cc6de6796f4c48ee9dfac901e915f299c75188995f84fd9df48de61031209263`.
