"""Validate a saved fixed-offset run and plot its actual CSV measurements.

Usage: python analyze_gps_offset.py results/gps_fixed_offset_<timestamp>
Requires matplotlib for plotting; this script does not connect to CARLA.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def separation(row):
    lat1 = math.radians(float(row["clean_latitude"]))
    lat2 = math.radians(float(row["reported_latitude"]))
    dlon = math.radians(float(row["reported_longitude"]) - float(row["clean_longitude"]))
    a = math.sin((lat2 - lat1) / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    return 2 * 6378137.0 * math.asin(math.sqrt(min(1.0, max(0.0, a))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_folder", type=Path)
    args = parser.parse_args()
    folder = args.run_folder
    with (folder / "readings.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    metadata = json.loads((folder / "metadata.json").read_text())
    if not rows:
        raise ValueError("CSV contains no measurements.")
    clean = [r for r in rows if r["phase"] == "clean"]
    attacked = [r for r in rows if r["phase"] == "attack"]
    numeric = [c for c in rows[0] if c != "phase"]
    finite = all(math.isfinite(float(r[c])) for r in rows for c in numeric)
    if not finite or not clean or not attacked:
        raise ValueError("Both phases and finite numeric data are required.")
    distances = [separation(r) for r in rows]
    attack_distances = [separation(r) for r in attacked]
    times = [float(r["elapsed_seconds"]) for r in rows]
    frames = [int(r["frame"]) for r in rows]
    same = lambda r: all(float(r["clean_" + c]) == float(r["reported_" + c])
                         for c in ("latitude", "longitude", "altitude"))
    start_xyz = [float(rows[0]["sensor_" + c]) for c in "xyz"]
    max_motion = max(math.sqrt(sum((float(r["sensor_" + c]) - start_xyz[i])**2
                                   for i, c in enumerate("xyz"))) for r in rows)
    onset = float(metadata["clean_seconds"])
    offset = float(metadata["offset_x_metres"])
    checks = {
        "all_numeric_values_finite": finite,
        "all_rows_have_valid_phase": len(clean) + len(attacked) == len(rows),
        "clean_coordinates_unchanged": all(same(r) for r in clean),
        "all_attacked_coordinates_changed": all(not same(r) for r in attacked),
        "clean_offsets_zero": all(float(r["offset_x_metres"]) == 0 for r in clean),
        "attack_offsets_match_settings": all(float(r["offset_x_metres"]) == offset for r in attacked),
        "phase_matches_simulation_time": all((r["phase"] == "attack") == (t >= onset)
                                              for r, t in zip(rows, times)),
        "simulation_times_strictly_increasing": all(b > a for a, b in zip(times, times[1:])),
        "frames_strictly_increasing": all(b > a for a, b in zip(frames, frames[1:])),
        "counts_match_metadata": metadata["sample_counts"] == {"clean": len(clean), "attack": len(attacked)},
        "horizontal_offset_within_1cm": all(abs(d - abs(offset)) < 0.01 for d in attack_distances),
        "sensor_motion_below_1mm": max_motion < 0.001,
        "recording_completed": metadata["status"] == "recording_completed",
    }
    summary = {
        "interpretation": "GPS-output manipulation verified; no driving or VLA effect evaluated",
        "checks": checks, "all_checks_passed": all(checks.values()),
        "total_readings": len(rows), "clean_readings": len(clean), "attacked_readings": len(attacked),
        "first_attacked_elapsed_seconds": float(attacked[0]["elapsed_seconds"]),
        "last_elapsed_seconds": times[-1], "max_recorded_sensor_motion_metres": max_motion,
        "approx_attack_horizontal_separation_metres": {"min": min(attack_distances), "max": max(attack_distances)},
        "distance_method": "Haversine spherical approximation, radius 6378137 m; not an ellipsoidal geodesic",
        "source_sha256": {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
                          for name in ("readings.csv", "metadata.json")},
    }
    (folder / "validation.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if not summary["all_checks_passed"]:
        raise ValueError("Validation failed; inspect validation.json before reporting success.")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, ax = plt.subplots(figsize=(10, 5.4), layout="constrained")
    total = onset + float(metadata["attack_seconds"])
    ax.axvspan(onset, total, color="#fff0e8", zorder=0)
    for phase, color, label in (("clean", "#167d8d", "Clean phase (50 readings)"),
                                ("attack", "#c34b25", "Offset phase (51 readings)")):
        indices = [i for i, r in enumerate(rows) if r["phase"] == phase]
        label = ("Clean" if phase == "clean" else "Offset") + " phase (" + str(len(indices)) + " readings)"
        ax.plot([times[i] for i in indices], [distances[i] for i in indices],
                color=color, marker="o", markersize=3.3, linewidth=1.6, label=label)
    ax.axvline(onset, color="#666666", linestyle="--", linewidth=1)
    ax.text(onset + 0.15, 5.65, "Offset enabled", color="#7e351c")
    ax.set(xlim=(0, total), ylim=(-0.45, 6.2), xticks=range(int(total) + 1),
           yticks=range(7), xlabel="Elapsed simulation time (seconds)",
           ylabel="Original-to-reported GPS separation (metres)",
           title="Fixed GPS offset: original and manipulated readings differ by 5 metres")
    ax.grid(axis="y", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="center left", frameon=False)
    fig.supxlabel("Parked vehicle | CARLA 0.9.14 | One run | No controller or VLA connected", fontsize=10)
    fig.savefig(folder / "gps_offset_plot.png", dpi=180)
    fig.savefig(folder / "gps_offset_plot.svg")
    plt.close(fig)


if __name__ == "__main__":
    main()
