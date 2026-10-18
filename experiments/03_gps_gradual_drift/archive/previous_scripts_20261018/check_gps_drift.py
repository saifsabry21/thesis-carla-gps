"""Check recorded gradual-drift data; no CARLA or third-party packages required.

Usage: python check_gps_drift.py results/gps_gradual_drift_<timestamp>
Add --plot on a computer with Matplotlib to also save a PNG and SVG graph.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def distance(row):
    a = math.radians(float(row['clean_latitude']))
    b = math.radians(float(row['reported_latitude']))
    dlon = math.radians(float(row['reported_longitude']) - float(row['clean_longitude']))
    h = math.sin((b - a) / 2)**2 + math.cos(a) * math.cos(b) * math.sin(dlon / 2)**2
    return 12756274.0 * math.asin(math.sqrt(min(1.0, max(0.0, h))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_folder', type=Path)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    folder = args.run_folder
    metadata = json.loads((folder / 'metadata.json').read_text())
    with (folder / 'readings.csv').open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    if not rows or metadata.get('attack_type') != 'linear_gps_drift':
        raise ValueError('Expected a completed gradual-drift run with measurements.')
    if not all(math.isfinite(float(v)) for r in rows for k, v in r.items() if k != 'phase'):
        raise ValueError('CSV contains non-finite numeric values.')
    clean_duration = float(metadata['clean_seconds'])
    drift_duration = float(metadata['drift_seconds'])
    maximum = float(metadata['max_offset_x_metres'])
    total_duration = clean_duration + drift_duration + float(metadata['hold_seconds'])
    groups = {p: [r for r in rows if r['phase'] == p] for p in ('clean', 'drift', 'hold')}
    times = [float(r['elapsed_seconds']) for r in rows]
    actual_offsets = [float(r['offset_x_metres']) for r in rows]
    distances = [distance(r) for r in rows]
    expected = [min(max((t - clean_duration) / drift_duration, 0.0), 1.0) * maximum for t in times]
    phases = ['clean' if t < clean_duration else 'drift' if t < clean_duration + drift_duration else 'hold' for t in times]
    same = lambda r: all(float(r['clean_' + c]) == float(r['reported_' + c]) for c in ('latitude', 'longitude', 'altitude'))
    first_xyz = [float(rows[0]['sensor_' + c]) for c in 'xyz']
    movement = max(math.sqrt(sum((float(r['sensor_' + c]) - first_xyz[i])**2 for i, c in enumerate('xyz'))) for r in rows)
    checks = {
        'recording_completed': metadata['status'] == 'recording_completed',
        'all_three_phases_present': all(groups.values()),
        'counts_match_metadata': {p: len(g) for p, g in groups.items()} == metadata['sample_counts'],
        'phases_match_timing': [r['phase'] for r in rows] == phases,
        'timestamps_increase': all(b > a for a, b in zip(times, times[1:])),
        'recording_starts_at_zero': abs(times[0]) < 1e-6,
        'recorded_samples_inside_interval': all(0 <= t < total_duration for t in times),
        'offset_follows_linear_profile': all(abs(a - e) < 1e-8 for a, e in zip(actual_offsets, expected)),
        'clean_coordinates_preserved': bool(groups['clean']) and all(same(r) for r in groups['clean']),
        'horizontal_separation_matches_offset_within_1cm': all(abs(d - abs(e)) < 0.01 for d, e in zip(distances, expected)),
        'recorded_sensor_motion_below_1mm': movement < 0.001,
        'altitude_preserved': all(float(r['clean_altitude']) == float(r['reported_altitude']) for r in rows),
    }
    report = {
        'all_checks_passed': all(checks.values()), 'checks': checks,
        'total_readings': len(rows), 'sample_counts': {p: len(g) for p, g in groups.items()},
        'max_applied_offset_metres': max(actual_offsets),
        'max_approx_horizontal_separation_metres': max(distances),
        'max_recorded_sensor_movement_metres': movement,
        'distance_method': 'Spherical Haversine approximation with radius 6378137 m',
        'interpretation': 'GPS-output drift test only; no controller/VLA effect evaluated',
        'source_sha256': {n: hashlib.sha256((folder / n).read_bytes()).hexdigest() for n in ('readings.csv', 'metadata.json')},
    }
    (folder / 'validation.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if not report['all_checks_passed']:
        raise ValueError('Some checks failed. Inspect the report before claiming a verified run.')
    if args.plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 5.4), layout='constrained')
        ax.axvspan(clean_duration, clean_duration + drift_duration, color='#fff0e8')
        ax.axvspan(clean_duration + drift_duration, total_duration, color='#fbe2d6')
        ax.plot(times, distances, color='#c34b25', marker='.', markersize=4, linewidth=1.5,
                label='Measured original-to-reported GPS separation')
        for t in (clean_duration, clean_duration + drift_duration):
            ax.axvline(t, color='#777777', linestyle='--', linewidth=1)
        for x, label in ((clean_duration / 2, 'CLEAN'),
                         (clean_duration + drift_duration / 2, 'GRADUAL DRIFT'),
                         (clean_duration + drift_duration + float(metadata['hold_seconds']) / 2, 'HOLD')):
            ax.text(x, maximum * 1.1, label, ha='center', fontsize=10)
        ax.set(xlim=(0, total_duration), ylim=(-0.5, maximum * 1.2),
               xlabel='Elapsed simulation time (seconds)',
               ylabel='GPS position difference (metres)',
               title='Gradual GPS drift: false position moves away while the car stays parked')
        ax.grid(axis='y', alpha=0.2)
        ax.spines[['top', 'right']].set_visible(False)
        fig.supxlabel('Actual recorded data. GPS-output manipulation only; no controller or VLA connected.', fontsize=10)
        for suffix in ('png', 'svg'):
            fig.savefig(folder / ('gps_drift_plot.' + suffix), dpi=180)
        plt.close(fig)


if __name__ == '__main__':
    main()
