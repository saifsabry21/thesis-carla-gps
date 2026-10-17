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
