# 03 - Fixed GPS offset with CARLA visuals

**Status: GPS-output manipulation and visual demonstration verified. Driving effects not tested.**

This performs the same five-metre offset as experiment 02 and adds real/false-position markers and a viewing pause. It is not just an animation: it saves original and manipulated GPS coordinates.

- `gps_offset_visual.py`: executed visual experiment source, unchanged.
- `analyze_gps_offset.py`: identical copy of the fixed-offset analysis helper, included here so this folder is self-contained.
- [Recorded run and notes](results/gps_offset_visual_20261017T214633_130642Z/EXPERIMENT_NOTES.md): original CSV, settings, validation, graph, and CARLA screenshot.
- [CARLA screenshot](results/gps_offset_visual_20261017T214633_130642Z/carla_visual_screenshot.png).

## Run on the university PC

Follow [setup](../../setup/START_HERE.md), then:

```bash
conda activate carla
cd ~/thesis-gps
python -u gps_offset_visual.py
```

Press Enter at the first prompt to start. At the final prompt, leave the script waiting while viewing or capturing CARLA. Press Enter again to remove its test objects and finalize metadata.

Green marks the real position; red marks the false reported GPS position. The arrow shows a location error, not a path driven by the car. The current recorded visual has strong red glow; the new drift script uses thinner marks, but its appearance is not yet tested.

Analyze this run from this experiment folder with Matplotlib available:

```bash
python analyze_gps_offset.py results/gps_offset_visual_20261017T214633_130642Z
```
