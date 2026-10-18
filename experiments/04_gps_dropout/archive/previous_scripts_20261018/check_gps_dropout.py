"""Check a GPS dropout run without importing CARLA; optional --plot needs matplotlib."""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


def validate(folder):
    metadata = json.loads((folder / "metadata.json").read_text())
    with (folder / "readings.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("The CSV contains no sensor readings.")
    clean = float(metadata["clean_seconds"])
    dropout = float(metadata["dropout_seconds"])
    duration = clean + dropout + float(metadata["recovery_seconds"])
    times = [float(r["elapsed_seconds"]) for r in rows]
    stamps = [float(r["simulation_time"]) for r in rows]
    frames = [int(r["frame"]) for r in rows]
    phases = [r["phase"] for r in rows]
    counts = dict(Counter(phases))
    axes = ("latitude", "longitude", "altitude")
    expected = ["clean" if t < clean else "dropout" if t < clean+dropout else "recovery" for t in times]
    origin = [float(rows[0]["sensor_"+axis]) for axis in "xyz"]
    movement = max(math.sqrt(sum((float(r["sensor_"+a])-origin[i])**2
                                for i,a in enumerate("xyz"))) for r in rows)
    tick = float(metadata["sensor_tick_seconds"])
    checks = {
        "recording_completed": metadata["status"] == "recording_completed",
        "all_three_phases_present": set(phases) == {"clean", "dropout", "recovery"},
        "counts_match_metadata": counts == metadata["sample_counts"],
        "phases_match_timing": phases == expected,
        "timestamps_and_frames_increase": all(b>a for a,b in zip(stamps,stamps[1:])) and all(b>a for a,b in zip(frames,frames[1:])),
        "elapsed_matches_simulation_clock": all(abs(t-(s-stamps[0])) < 1e-8 for t,s in zip(times,stamps)),
        "interval_covered": abs(times[0]) < 1e-8 and all(0 <= t < duration for t in times) and times[-1] >= duration-2*tick,
        "raw_samples_continue_through_dropout": all(b-a <= 3*tick for a,b in zip(stamps,stamps[1:])),
        "raw_coordinates_finite": all(math.isfinite(float(r["clean_"+a])) for r in rows for a in axes),
        "availability_matches_phase": all(r["output_available"] == ("0" if r["phase"]=="dropout" else "1") for r in rows),
        "dropout_coordinates_empty": all(r["reported_"+a] == "" for r in rows if r["phase"]=="dropout" for a in axes),
        "available_coordinates_match_current_raw_sample": all(r["reported_"+a] == r["clean_"+a] for r in rows if r["phase"]!="dropout" for a in axes),
        "recorded_sensor_motion_below_1mm": movement < .001,
    }
    report = {
        "all_checks_passed": all(checks.values()), "checks": checks,
        "total_readings": len(rows), "sample_counts": counts,
        "withheld_output_samples": sum(r["output_available"]=="0" for r in rows),
        "max_recorded_sensor_movement_metres": movement,
        "interpretation": "Software GPS-output dropout only; raw CARLA GNSS continues. No RF jamming or controller/VLA effect evaluated. A parked test cannot independently distinguish stale replay from current equal-valued coordinates.",
        "source_sha256": {name: hashlib.sha256((folder/name).read_bytes()).hexdigest()
                          for name in ("readings.csv", "metadata.json")},
    }
    return rows, report


def plot_run(folder, rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    times = [float(r["elapsed_seconds"]) for r in rows]
    available = [int(r["output_available"]) for r in rows]
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.step(times, available, where="post", color="#167A68", linewidth=2.5)
    missing = [float(r["elapsed_seconds"]) for r in rows if r["phase"]=="dropout"]
    ax.axvspan(min(missing), max(missing), color="#C43D3D", alpha=.12, label="Reported output withheld")
    ax.set(xlabel="Elapsed simulation time (seconds)", ylabel="Reported GPS availability",
           title="GPS output dropout: normal → missing → restored", ylim=(-.15,1.25))
    ax.set_yticks([0,1], labels=["Missing", "Available"])
    ax.grid(alpha=.2)
    ax.legend(loc="upper center")
    fig.text(.5,.01,"Raw GNSS remained logged. Parked car; no controller or VLA tested.",ha="center",fontsize=9)
    fig.tight_layout(rect=(0,.04,1,1))
    for extension in ("png","svg"):
        fig.savefig(folder/("gps_dropout_plot."+extension),dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    rows, report = validate(args.folder)
    (args.folder/"validation.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
    if args.plot and report["all_checks_passed"]:
        plot_run(args.folder,rows)
        print("Graph saved in:",args.folder)
    raise SystemExit(0 if report["all_checks_passed"] else 1)


if __name__ == "__main__":
    main()
