# 02 - Fixed GPS position offset

**Status: GPS-output manipulation verified. Driving effects not tested.**

The script records five clean simulation seconds followed by five seconds with a +5 m map-X offset in its reported GPS output. The physical car stays parked.

- `gps_fixed_offset.py`: executed experiment source, unchanged.
- `analyze_gps_offset.py`: checker and graph generator for saved fixed-offset data; requires Matplotlib.
- [Recorded run and full notes](results/gps_fixed_offset_20261017T211819_023749Z/EXPERIMENT_NOTES.md): 50 clean and 51 manipulated readings, settings, validation, and graphs.

## Run on the university PC

Follow [setup](../../setup/START_HERE.md), then:

```bash
conda activate carla
cd ~/thesis-gps
python -u gps_fixed_offset.py
```

Each run saves its own folder under `results/` beside the source. This simpler version removes the test objects automatically after recording. Use experiment 03 for a visual demonstration that waits for screenshots.

For local analysis from this experiment folder, with Matplotlib available:

```bash
python analyze_gps_offset.py results/gps_fixed_offset_20261017T211819_023749Z
```
