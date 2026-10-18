# Thesis 1 work

Start with [setup/START_HERE.md](setup/START_HERE.md) when you connect to the university PC.

## Your experiments

| Folder | What it contains | Current status |
|---|---|---|
| [01 GPS baseline](experiments/01_gps_baseline/README.md) | Original no-attack script and 100-reading dataset | Verified |
| [02 Fixed GPS offset](experiments/02_gps_fixed_offset/README.md) | Five-metre step offset, CSV, settings, graph, and notes | Verified at GPS-output level |
| [03 Visual fixed GPS offset](experiments/03_gps_fixed_offset_visual/README.md) | Same manipulation with CARLA markers, screenshot, and its own results | Verified at GPS-output level |
| [04 Gradual GPS drift](experiments/04_gps_gradual_drift/README.md) | Visual drift script, checker, and instructions | First run verified at GPS-output level |

Each experiment has its own script and `results/` folder. Completed runs retain their original timestamped folders. The visual experiment also includes a copy of the shared fixed-offset analysis script so it can be checked from its own folder.

## Other folders

- **setup:** startup instructions, connection checks, and machine details.
- **project_notes:** current progress, provenance, and the folder-move record.
- **archive:** the existing ZIP backup and earlier layout notes, preserved unchanged.

## What is currently demonstrated

The experiments modify GPS output reported by our Python program. The physical car remains parked, and no driving controller or VLA has received the false coordinates yet. The arrow illustrates a position error, not a driven path.

## Laptop and university PC

This folder structure is on your Windows laptop. The university scripts still live in `/home/g02-f26/thesis-gps/`, so the setup guide uses that path. Transfer the needed Python files into that directory through RustDesk. Completed remote run folders can then be copied into the corresponding laptop experiment's `results/` folder.

The laptop, university PC, GitHub, and ZIP backups do not synchronize automatically. The GitHub repository now uses this organized layout, including the completed gradual-drift run and startup guides. The preserved ZIP predates the new drift-preparation files.

See [current progress and next work](project_notes/PROGRESS.md).
