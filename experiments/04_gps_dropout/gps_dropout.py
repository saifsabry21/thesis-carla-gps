"""GPS dropout: live attack, shapes, automatic checks, SVG chart and recorded review.

Run:     python -u gps_dropout.py
Replay:  python -u gps_dropout.py --replay results/gps_dropout_TIMESTAMP
Check:   python gps_dropout.py --check results/gps_dropout_TIMESTAMP

CARLA 0.9.14; parked vehicle, output gate only, no controller/VLA.
API: https://carla.readthedocs.io/en/0.9.14/python_api/
"""
import argparse
import csv
import hashlib
import json
import math
import queue
import threading
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

VERSION = "2.0"
CLEAN_SECONDS = DROPOUT_SECONDS = RECOVERY_SECONDS = 5.0
PHASES = ("clean", "dropout", "recovery")

def attack_profile(elapsed):
    """Simulation-time phases; the gate drops output, never the raw log."""
    if elapsed < CLEAN_SECONDS:
        return "clean", True
    if elapsed < CLEAN_SECONDS + DROPOUT_SECONDS:
        return "dropout", False
    return "recovery", True

def reported_output(latitude, longitude, altitude, available):
    """None values become empty CSV cells; no fabricated zero coordinates."""
    return (latitude, longitude, altitude) if available else (None, None, None)

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

def save_json(path, value):
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def save_chart(folder, rows):
    """Standalone SVG, no plotting packages needed. Draw actual sample timestamps."""
    elapsed = [float(r["elapsed_seconds"]) for r in rows]
    available = [int(r["output_available"]) for r in rows]
    duration = max(elapsed[-1], 1)
    def x(t):
        return 100 + 720*t/duration
    def y(value):
        return 110 if value else 260
    points = ["{:.2f},{}".format(x(elapsed[0]), y(available[0]))]
    for index in range(1, len(rows)):
        points += ["{:.2f},{}".format(x(elapsed[index]),y(available[index-1])),
                   "{:.2f},{}".format(x(elapsed[index]),y(available[index]))]
    ticks = "".join('<text x="{:.2f}" y="305" text-anchor="middle">{:.1f}</text>'.format(x(t),t)
                    for t in (0,5,10,elapsed[-1]))
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="380" viewBox="0 0 900 380">
<rect width="900" height="380" fill="#fff"/>
<g font-family="Arial,sans-serif" fill="#152738" font-size="15">
<text x="450" y="36" text-anchor="middle" font-size="23">Recorded GPS output availability</text>
<text x="450" y="62" text-anchor="middle">Normal → Dropout → Recovery</text>
<path d="M100 90 V280 H830" fill="none" stroke="#87939e"/>
<text x="92" y="116" text-anchor="end">Available</text>
<text x="92" y="266" text-anchor="end">Missing</text>
<polyline points="POINTS" fill="none" stroke="#008568" stroke-width="4"/>
TICKS
<text x="460" y="335" text-anchor="middle">Elapsed simulation time (seconds)</text>
<text x="450" y="367" text-anchor="middle" font-size="13">Raw GNSS kept logging. Parked vehicle; no controller or VLA evaluated.</text>
</g></svg>'''.replace("POINTS", " ".join(points)).replace("TICKS", ticks)
    (folder/"gps_dropout_plot.svg").write_text(svg,encoding="utf-8")


def check_and_save(folder):
    rows, report = validate(folder)
    # Preserve an existing checker report from the original experiment.
    target = folder/("validation_unified.json" if (folder/"validation.json").exists() else "validation.json")
    save_json(target,report)
    print(json.dumps(report,indent=2))
    if not report["all_checks_passed"]:
        raise RuntimeError("Validation failed. Keep partial results; do not claim success.")
    save_chart(folder,rows)
    summary = ("# GPS output dropout — recorded result\n\n"
               "All {} checks passed.\n\n".format(len(report["checks"])) +
               "Samples: {}. Withheld reported outputs: {}.\n\n".format(report["sample_counts"],report["withheld_output_samples"]) +
               "Maximum recorded sensor movement: {} m.\n\n".format(report["max_recorded_sensor_movement_metres"]) +
               "The output gate withholds reported coordinates during dropout. Original CARLA GNSS keeps logging. "
               "There is no RF interference and no driving controller or VLA consumes the attacked output.\n\n"
               "Green ring: available output. Red cross: missing output. Blue outline: parked vehicle. "
               "A guided review is explicitly labeled as a replay, not an additional attack trial.\n")
    (folder/"RESULT_SUMMARY.md").write_text(summary,encoding="utf-8")
    print("Validation, chart and summary saved in:",folder)
    return rows,report


class Visuals:
    def __init__(self, carla, world, position, yaw):
        self.carla,self.world,self.position,self.yaw=carla,world,position,yaw
        self.state=("clean","READY - PRESS ENTER IN TERMINAL",0)
        self.error=None
        self.stop=threading.Event()
        self.thread=threading.Thread(target=self.draw,daemon=True)

    def draw(self):
        c=self.carla
        palette={"green":c.Color(r=0,g=200,b=0,a=255),
                 "red":c.Color(r=220,g=0,b=0,a=255),"blue":c.Color(r=0,g=0,b=255,a=255)}
        p=self.position
        try:
            while not self.stop.is_set():
                phase,title,count=self.state
                label={"clean":"GPS AVAILABLE - RING","dropout":"GPS UNAVAILABLE - CROSS",
                       "recovery":"GPS RESTORED - RING"}[phase]
                for begin,end,color in shape_segments(p.x,p.y,p.z,self.yaw,phase):
                    self.world.debug.draw_line(c.Location(*begin),c.Location(*end),
                        thickness=.09 if color=="blue" else .16,color=palette[color],life_time=.18)
                for dx,text in [(7,title),(6,label+" | {} samples".format(count)),
                                (-6,"BLUE OUTLINE = REAL CAR | NO CONTROLLER/VLA")]:
                    self.world.debug.draw_string(c.Location(x=p.x+dx,y=p.y-5,z=p.z+3),text,
                        draw_shadow=True,color=c.Color(255,255,255),life_time=.18)
                self.stop.wait(.10)
        except Exception as exc:
            self.error=str(exc)
            print("Visual drawing failed:",exc)

    def close(self):
        self.stop.set()
        self.thread.join(timeout=3)


def record(carla,client,world,car,visuals):
    settings=world.get_settings()
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    folder=Path(__file__).resolve().parent/"results"/("gps_dropout_"+stamp)
    folder.mkdir(parents=True,exist_ok=False)
    p=car.get_location()
    metadata=dict(status="started",started_utc=stamp,map=world.get_map().name,
        client_version=client.get_client_version(),server_version=client.get_server_version(),
        synchronous_mode=settings.synchronous_mode,fixed_delta_seconds=settings.fixed_delta_seconds,
        attack_type="gps_output_dropout",clean_seconds=5.0,dropout_seconds=5.0,recovery_seconds=5.0,
        dropout_representation="output_available=false; reported coordinates empty",
        recovery_policy="pass current sample; no stale replay",sensor_tick_seconds=.1,
        gnss_noise_bias_and_stddev=0.0,scope="GNSS output manipulation only; no driving consumer",
        vehicle_id=car.id,vehicle_start_xyz=[p.x,p.y,p.z],script_version=VERSION,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        visualization="Live ring/cross/outline during recording; guided recorded review afterward")
    counts=dict.fromkeys(PHASES,0)
    sensor=None
    listening=False
    started_wall=time.monotonic()
    try:
        bp=world.get_blueprint_library().find("sensor.other.gnss")
        bp.set_attribute("sensor_tick","0.1")
        for axis in ("lat","lon","alt"):
            for parameter in ("bias","stddev"):
                bp.set_attribute("noise_"+axis+"_"+parameter,"0.0")
        sensor=world.spawn_actor(bp,carla.Transform(carla.Location(z=1.5)),attach_to=car)
        samples=queue.Queue()
        sensor.listen(samples.put)
        listening=True
        print("LIVE ATTACK: 5 clean + 5 dropout + 5 recovery SIMULATION seconds.")
        print("Results folder:",folder)
        origin=None
        previous=None
        fields=["frame","simulation_time","elapsed_seconds","phase","output_available",
                "sensor_x","sensor_y","sensor_z","clean_latitude","clean_longitude","clean_altitude",
                "reported_latitude","reported_longitude","reported_altitude"]
        with (folder/"readings.csv").open("w",newline="") as handle:
            writer=csv.writer(handle)
            writer.writerow(fields)
            while True:
                if time.monotonic()-started_wall > 120:
                    raise RuntimeError("Recording exceeded 120 wall seconds.")
                try:
                    data=samples.get(timeout=10)
                except queue.Empty:
                    raise RuntimeError("No raw GNSS sample received for 10 wall seconds.")
                if origin is None:
                    origin=data.timestamp
                elapsed=data.timestamp-origin
                if elapsed >= 15:
                    break
                phase,available=attack_profile(elapsed)
                actual=data.transform.location
                output=reported_output(data.latitude,data.longitude,data.altitude,available)
                writer.writerow([data.frame,data.timestamp,elapsed,phase,int(available),
                    actual.x,actual.y,actual.z,data.latitude,data.longitude,data.altitude,*output])
                counts[phase]+=1
                visuals.state=(phase,"LIVE GPS OUTPUT ATTACK | t={:.1f}s".format(elapsed),counts[phase])
                if phase!=previous:
                    print("Phase:",phase,"| simulation elapsed:",round(elapsed,3),"| available:",available)
                    previous=phase
        if not all(counts.values()):
            raise RuntimeError("A phase contains no samples.")
        metadata["status"]="recording_completed"
    except BaseException as exc:
        metadata["status"]="interrupted" if isinstance(exc,(KeyboardInterrupt,EOFError)) else "failed"
        metadata["error"]=str(exc)
        raise
    finally:
        # Stop exactly once; do not depend on is_listening updating immediately.
        cleanup=[]
        if sensor is not None:
            if listening:
                try:
                    sensor.stop()
                except Exception as exc:
                    cleanup.append("sensor.stop: "+str(exc))
            try:
                sensor.destroy()
            except Exception as exc:
                cleanup.append("sensor.destroy: "+str(exc))
        metadata["sample_counts"]=counts
        metadata["recording_wall_seconds"]=time.monotonic()-started_wall
        metadata["sensor_cleanup_notes"]=cleanup
        save_json(folder/"metadata.json",metadata)
    print("Recording finished:",counts)
    return folder


def guided_review(visuals,folder,report):
    print("\nRECORDED REVIEW:",folder.name,"(not a new attack)")
    for phase in PHASES:
        count=report["sample_counts"][phase]
        visuals.state=(phase,"RECORDED RESULT REPLAY - NOT A LIVE ATTACK",count)
        print("Showing:",phase,"|",count,"recorded samples")
        input("Inspect CARLA / take screenshot. Press Enter HERE for the next stage...")
        if visuals.error:
            raise RuntimeError("Visual drawing failed: "+visuals.error)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument("--check",type=Path,metavar="RESULT_FOLDER")
    modes.add_argument("--replay",type=Path,metavar="RESULT_FOLDER")
    args=parser.parse_args()
    if args.check:
        check_and_save(args.check.resolve())
        return
    report=None
    folder=None
    if args.replay:
        folder=args.replay.resolve()
        _,report=check_and_save(folder)
    import carla
    client=carla.Client("localhost",2000)
    client.set_timeout(20)
    world=client.get_world()
    if world.get_settings().synchronous_mode:
        raise RuntimeError("World is synchronous. Do not change a teammate's settings.")
    if folder and world.get_map().name!=json.loads((folder/"metadata.json").read_text())["map"]:
        raise RuntimeError("Current map differs from the recording's map.")
    car=None
    visuals=None
    try:
        bp=world.get_blueprint_library().find("vehicle.tesla.model3")
        for spawn in world.get_map().get_spawn_points():
            car=world.try_spawn_actor(bp,spawn)
            if car is not None:
                break
        if car is None:
            raise RuntimeError("No free vehicle spawn point.")
        car.apply_control(carla.VehicleControl(brake=1,hand_brake=True))
        time.sleep(2)
        p=car.get_location()
        world.get_spectator().set_transform(carla.Transform(
            carla.Location(x=p.x+2,y=p.y+1,z=p.z+25),carla.Rotation(pitch=-90)))
        visuals=Visuals(carla,world,p,car.get_transform().rotation.yaw)
        visuals.thread.start()
        if folder is None:
            input("Car ready. Press Enter HERE to run attack; switch to CARLA to watch...")
            folder=record(carla,client,world,car,visuals)
            _,report=check_and_save(folder)
        guided_review(visuals,folder,report)
    finally:
        if visuals is not None:
            visuals.close()
        if car is not None:
            car.destroy()
        print("Experiment vehicle removed. Results kept.")


if __name__=="__main__":
    main()
