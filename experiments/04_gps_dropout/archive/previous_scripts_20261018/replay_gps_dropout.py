"""Replay saved dropout phases in CARLA. Does not execute a new attack."""
import argparse
import csv
import json
import threading
import time
from collections import Counter
from pathlib import Path

import carla


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    metadata = json.loads((args.folder / "metadata.json").read_text())
    with (args.folder / "readings.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if metadata["status"] != "recording_completed":
        raise RuntimeError("This recording did not complete.")
    counts = dict(Counter(row["phase"] for row in rows))
    if set(counts) != {"clean", "dropout", "recovery"} or counts != metadata["sample_counts"]:
        raise RuntimeError("Missing phases or sample counts disagree with metadata.")
    for row in rows:
        available = row["phase"] != "dropout"
        if row["output_available"] != str(int(available)):
            raise RuntimeError("Availability does not match the recorded phase.")
        for axis in ("latitude", "longitude", "altitude"):
            expected = row["clean_" + axis] if available else ""
            if row["reported_" + axis] != expected:
                raise RuntimeError("Reported coordinates do not match the expected gate output.")

    client = carla.Client("localhost", 2000)
    client.set_timeout(20)
    world = client.get_world()
    if world.get_map().name != metadata["map"]:
        raise RuntimeError("Load the recording's map before replaying it.")
    if world.get_settings().synchronous_mode:
        raise RuntimeError("World is synchronous; do not change a teammate's settings.")
    car = None
    stop = threading.Event()
    state = [None]
    thread = None

    def draw():
        while not stop.is_set():
            current = state[0]
            if current is not None:
                location, phase = current
                color = carla.Color(20, 230, 50) if phase != "dropout" else carla.Color(240, 25, 20)
                label = {"clean": "GPS AVAILABLE", "dropout": "GPS OUTPUT MISSING",
                         "recovery": "GPS OUTPUT RESTORED"}[phase]
                try:
                    # The light is an availability indicator, NOT a GPS position.
                    world.debug.draw_point(carla.Location(x=location.x+4, y=location.y,
                                                          z=location.z+3),
                                           size=0.65, color=color, life_time=1.0)
                    for dx, text in [(7, "SAVED RESULT REPLAY - NOT A LIVE ATTACK"),
                                     (6, label + " | {} recorded samples".format(counts[phase])),
                                     (5, "COLORED LIGHT = OUTPUT STATUS, NOT POSITION"),
                                     (-3, "REAL CAR - NO CONTROLLER OR VLA")]:
                        world.debug.draw_string(
                            carla.Location(x=location.x+dx, y=location.y-4, z=location.z+3),
                            text, draw_shadow=True, color=carla.Color(255,255,255), life_time=1.0)
                except RuntimeError as exc:
                    print("Visualization stopped:", exc)
                    return
            stop.wait(0.05)

    try:
        blueprint = world.get_blueprint_library().find("vehicle.tesla.model3")
        for spawn in world.get_map().get_spawn_points():
            car = world.try_spawn_actor(blueprint, spawn)
            if car is not None:
                break
        if car is None:
            raise RuntimeError("No free vehicle spawn point.")
        car.apply_control(carla.VehicleControl(brake=1, hand_brake=True))
        time.sleep(2)
        position = car.get_location()
        world.get_spectator().set_transform(carla.Transform(
            carla.Location(x=position.x+2, y=position.y, z=position.z+24),
            carla.Rotation(pitch=-90)))
        state[0] = (position, "clean")
        thread = threading.Thread(target=draw, daemon=True)
        thread.start()
        print("Showing saved results from:", args.folder.name)
        print("This is a phase-by-phase replay. The original CSV is not changed.")
        for phase in ("clean", "dropout", "recovery"):
            state[0] = (position, phase)
            print("\nREPLAY:", phase.upper(), "| Recorded samples:", counts[phase])
            print("Light:", "RED (missing output)" if phase == "dropout" else "GREEN (available output)")
            input("Look at CARLA and take your screenshot. Press Enter HERE to continue...")
    finally:
        stop.set()
        if thread is not None:
            thread.join(timeout=2)
        if car is not None:
            car.destroy()
        print("Replay finished; its vehicle removed. Original recording unchanged.")


if __name__ == "__main__":
    main()
