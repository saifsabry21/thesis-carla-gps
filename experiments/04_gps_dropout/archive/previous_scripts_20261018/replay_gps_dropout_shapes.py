"""Replay recorded dropout using a ring, cross and car outline in CARLA. Does not execute a new attack."""
import argparse
import csv
import json
import math
import threading
import time
from collections import Counter
from pathlib import Path

import carla


def shape_segments(x, y, z, yaw, phase):
    """Return world-space line segments. Shapes encode status, not GPS error."""
    angle = math.radians(yaw)
    def point(u, v):
        return (x + u*math.cos(angle) - v*math.sin(angle),
                y + u*math.sin(angle) + v*math.cos(angle), z + 2.8)
    segments = []
    # Persistent outline identifies the parked illustration vehicle.
    corners = [(-2.6,-1.3),(2.6,-1.3),(2.6,1.3),(-2.6,1.3)]
    for index in range(4):
        segments.append((point(*corners[index]), point(*corners[(index+1)%4]), "blue"))
    if phase == "dropout":
        # A separate cross denotes unavailable output, never a false position.
        for start,end in [((-1.7,3.5),(1.7,6.9)),((-1.7,6.9),(1.7,3.5))]:
            segments.append((point(*start), point(*end), "red"))
    else:
        for index in range(32):
            a = 2*math.pi*index/32
            b = 2*math.pi*(index+1)/32
            segments.append((point(3.7*math.cos(a),3.7*math.sin(a)),
                             point(3.7*math.cos(b),3.7*math.sin(b)), "green"))
    return segments


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
        palette = {"green": carla.Color(r=0,g=200,b=0,a=255),
                   "red": carla.Color(r=220,g=0,b=0,a=255),
                   "blue": carla.Color(r=0,g=0,b=255,a=255)}
        while not stop.is_set():
            current = state[0]
            if current is not None:
                location, yaw, phase = current
                label = {"clean": "GPS AVAILABLE - RING",
                         "dropout": "GPS UNAVAILABLE - CROSS",
                         "recovery": "GPS RESTORED - RING"}[phase]
                try:
                    for begin,end,color in shape_segments(location.x,location.y,location.z,yaw,phase):
                        world.debug.draw_line(carla.Location(*begin),carla.Location(*end),
                                              thickness=0.09 if color=="blue" else 0.16,
                                              color=palette[color],life_time=0.18)
                    for dx,text in [(7,"RECORDED RESULT REPLAY - NOT A LIVE ATTACK"),
                                    (6,label + " | {} samples".format(counts[phase])),
                                    (-6,"BLUE OUTLINE = REAL CAR | NO CONTROLLER/VLA")]:
                        world.debug.draw_string(
                            carla.Location(x=location.x+dx,y=location.y-5,z=location.z+3),
                            text,draw_shadow=True,color=carla.Color(255,255,255),life_time=0.18)
                except RuntimeError as exc:
                    print("Visualization stopped:",exc)
                    return
            stop.wait(0.10)

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
        yaw = car.get_transform().rotation.yaw
        world.get_spectator().set_transform(carla.Transform(
            carla.Location(x=position.x+2, y=position.y+1, z=position.z+25),
            carla.Rotation(pitch=-90)))
        state[0] = (position, yaw, "clean")
        thread = threading.Thread(target=draw, daemon=True)
        thread.start()
        print("Showing saved results from:", args.folder.name)
        print("This is a phase-by-phase replay. The original CSV is not changed.")
        for phase in ("clean", "dropout", "recovery"):
            state[0] = (position, yaw, phase)
            print("\nREPLAY:", phase.upper(), "| Recorded samples:", counts[phase])
            print("Shape:", "RED CROSS; GPS ring absent" if phase == "dropout" else "GREEN RING around car")
            print("Blue outline stays visible. Shapes indicate availability, not vehicle behavior.")
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
