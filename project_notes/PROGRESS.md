# Progress — 18 October 2026

All three attacks now use one script each and completed their combined-script runs.

- 02_gps_fixed_offset: gps_fixed_offset_20261018T123916_766224Z; {'clean': 51, 'attack': 49}; 14 checks passed remotely and locally.
- 03_gps_gradual_drift: gps_gradual_drift_20261018T124241_669723Z; {'clean': 51, 'drift': 100, 'hold': 49}; 14 checks passed remotely and locally.
- 04_gps_dropout: gps_dropout_20261018T122858_646455Z; {'clean': 50, 'dropout': 50, 'recovery': 50}; 13 checks passed remotely and locally.

Eight supplied screenshots archived with their exact recording and live/replay provenance. The verified raw hashes and executed-source hashes match. Recorded sensor movement was 0 m in the three combined runs. No controller or VLA effects have been evaluated. Google Doc unchanged.

## Simplified evidence folders

Each experiment now has one flat results folder. Fixed offset and drift retain their latest documented combined runs. Dropout uses the earlier verified run that matches its colored screenshots. All other complete runs and their reports remain in the per-experiment archive. See SELECTED_RESULTS.json for exact run identities and preserved-file hashes.
