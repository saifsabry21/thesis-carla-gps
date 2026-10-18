"""GPS offset: live attack, shapes, automatic checks, SVG chart and recorded review.

Run:     python -u gps_fixed_offset.py
Replay:  python -u gps_fixed_offset.py --replay results/gps_fixed_offset_TIMESTAMP
Check:   python gps_fixed_offset.py --check results/gps_fixed_offset_TIMESTAMP

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
MODE = 'fixed'
TITLE = 'Fixed GPS offset'
SETTINGS = {'clean_seconds': 5.0, 'attack_seconds': 5.0, 'offset_x_metres': 5.0}
MAXIMUM = 5.0
DURATION = 10
PHASES = ('clean', 'attack')

def attack_profile(elapsed, metadata=None):
    m = metadata or SETTINGS
    onset = float(m["clean_seconds"])
    if elapsed < onset:
        return "clean", 0.0
    if MODE == "fixed":
        return "attack", float(m["offset_x_metres"])
    drift = float(m["drift_seconds"])
    maximum = float(m["max_offset_x_metres"])
    if elapsed < onset + drift:
        return "drift", maximum * (elapsed-onset)/drift
    return "hold", maximum






def validate(folder):
    metadata=json.loads((folder/"metadata.json").read_text())
    with (folder/"readings.csv").open(newline="") as handle:
        rows=list(csv.DictReader(handle))
    if not rows or not all(math.isfinite(float(v)) for r in rows for k,v in r.items() if k!="phase"):
        raise ValueError("Expected nonempty, finite measurements.")
    times=[float(r["elapsed_seconds"]) for r in rows]
    stamps=[float(r["simulation_time"]) for r in rows]
    frames=[int(r["frame"]) for r in rows]
    expected=[attack_profile(t,metadata) for t in times]
    groups=Counter(r["phase"] for r in rows)
    duration=float(metadata["clean_seconds"])+(float(metadata["attack_seconds"]) if MODE=="fixed" else float(metadata["drift_seconds"])+float(metadata["hold_seconds"]))
    distances=[]
    for r in rows:
        lat1,lat2=[math.radians(float(r[k])) for k in ("clean_latitude","reported_latitude")]
        dlon=math.radians(float(r["reported_longitude"])-float(r["clean_longitude"]))
        h=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        distances.append(12756274*math.asin(math.sqrt(max(0,min(1,h)))))
    start=[float(rows[0]["sensor_"+a]) for a in "xyz"]
    motion=max(math.sqrt(sum((float(r["sensor_"+a])-start[i])**2 for i,a in enumerate("xyz"))) for r in rows)
    checks={
        "recording_completed":metadata["status"]=="recording_completed",
        "all_phases_present":set(groups)==set(PHASES),
        "counts_match_metadata":dict(groups)==metadata["sample_counts"],
        "phases_match_timing":[r["phase"] for r in rows]==[p for p,dx in expected],
        "frames_and_timestamps_increase":all(b>a for a,b in zip(frames,frames[1:])) and all(b>a for a,b in zip(stamps,stamps[1:])),
        "elapsed_matches_simulation_clock":all(abs(t-(s-stamps[0]))<1e-7 for t,s in zip(times,stamps)),
        "recording_starts_at_zero":abs(times[0])<1e-7,
        "samples_inside_interval":all(0<=t<duration for t in times),
        "recording_reaches_end":times[-1]>=duration-2*float(metadata["sensor_tick_seconds"]),
        "offset_matches_profile":all(abs(float(r["offset_x_metres"])-dx)<1e-8 for r,(p,dx) in zip(rows,expected)),
        "clean_coordinates_preserved":all(float(r["clean_"+a])==float(r["reported_"+a]) for r in rows if r["phase"]=="clean" for a in ("latitude","longitude","altitude")),
        "horizontal_separation_matches_offset_within_1cm":all(abs(d-abs(dx))<.01 for d,(p,dx) in zip(distances,expected)),
        "altitude_preserved":all(float(r["clean_altitude"])==float(r["reported_altitude"]) for r in rows),
        "recorded_sensor_motion_below_1mm":motion<.001,
    }
    return rows,dict(all_checks_passed=all(checks.values()),checks=checks,total_readings=len(rows),
        sample_counts=dict(groups),max_applied_offset_metres=max(float(r["offset_x_metres"]) for r in rows),
        max_approx_horizontal_separation_metres=max(distances),max_recorded_sensor_movement_metres=motion,
        distance_method="Spherical Haversine approximation, radius 6378137 m",
        interpretation="GPS-output manipulation only. No controller or VLA effect evaluated.",
        source_sha256={n:hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in ("readings.csv","metadata.json")})






def save_json(path, value):
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def save_chart(folder,rows):
    times=[float(r["elapsed_seconds"]) for r in rows]
    offsets=[float(r["offset_x_metres"]) for r in rows]
    top=max(max(offsets),1)
    def point(t,v): return "{:.2f},{:.2f}".format(90+740*t/max(times[-1],1),270-170*v/top)
    points=[point(times[0],offsets[0])]
    for i in range(1,len(rows)):
        if MODE=="fixed": points.append(point(times[i],offsets[i-1]))
        points.append(point(times[i],offsets[i]))
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="370"><rect width="900" height="370" fill="white"/><g font-family="Arial" fill="#172b3a" font-size="15"><text x="450" y="35" text-anchor="middle" font-size="23">'+TITLE+' — recorded output offset</text><path d="M90 80 V280 H840" stroke="#89939c" fill="none"/><polyline points="'+" ".join(points)+'" stroke="#c43d3d" stroke-width="3" fill="none"/>'
    svg+='<text x="82" y="275" text-anchor="end">0 m</text><text x="82" y="105" text-anchor="end">'+str(top)+' m</text>'
    for t in (0,5,times[-1]): svg+='<text x="'+str(90+740*t/max(times[-1],1))+'" y="305" text-anchor="middle">'+str(round(t,1))+'</text>'
    svg+='<text x="450" y="335" text-anchor="middle">Elapsed simulation time (seconds)</text><text x="450" y="360" text-anchor="middle" font-size="12">Map-X offset in metres. Parked car; no controller or VLA evaluated.</text></g></svg>'
    (folder/"gps_offset_plot.svg").write_text(svg,encoding="utf-8")




def check_and_save(folder):
    rows,report=validate(folder)
    target=folder/("validation_unified.json" if (folder/"validation.json").exists() else "validation.json")
    save_json(target,report)
    print(json.dumps(report,indent=2))
    if not report["all_checks_passed"]: raise RuntimeError("Validation failed; keep data for diagnosis.")
    save_chart(folder,rows)
    (folder/"RESULT_SUMMARY.md").write_text(
        "# "+TITLE+"\n\nAll "+str(len(report["checks"]))+" checks passed.\n\n"+
        "Samples: "+str(report["sample_counts"])+". Maximum applied map-X offset: "+str(report["max_applied_offset_metres"])+" m.\n\n"+
        "Maximum recorded sensor motion: "+str(report["max_recorded_sensor_movement_metres"])+" m.\n\n"+
        "Original sensor readings retained. Green = real position; red = reported position; arrow = position error, not trajectory. " +
        "Guided review is recorded replay. No controller or VLA consumes the attacked output.\n",encoding="utf-8")
    print("Validation, SVG chart and summary saved in:",folder)
    return rows,report




class Visuals:
    def __init__(self,carla,world,position,yaw):
        self.carla,self.world,self.position,self.yaw=carla,world,position,yaw
        self.state=("clean","READY - PRESS ENTER IN TERMINAL",0.0)
        self.error=None
        self.stop=threading.Event()
        self.thread=threading.Thread(target=self.draw,daemon=True)
    def draw(self):
        c=self.carla;p=self.position
        green=c.Color(r=0,g=200,b=0,a=255);red=c.Color(r=220,g=0,b=0,a=255)
        while not self.stop.is_set():
            phase,title,dx=self.state
            try:
                real=c.Location(x=p.x,y=p.y,z=p.z+2.8)
                false=c.Location(x=p.x+dx,y=p.y,z=p.z+2.8)
                for center,color in [(real,green)]+([(false,red)] if dx else []):
                    for i in range(16):
                        a,b=2*math.pi*i/16,2*math.pi*(i+1)/16
                        self.world.debug.draw_line(c.Location(x=center.x+.65*math.cos(a),y=center.y+.65*math.sin(a),z=center.z),c.Location(x=center.x+.65*math.cos(b),y=center.y+.65*math.sin(b),z=center.z),thickness=.06,color=color,life_time=.18)
                if dx:
                    self.world.debug.draw_arrow(real,false,thickness=.04,arrow_size=.22,color=red,life_time=.18)
                labels=[(p.x+MAXIMUM/2,p.y-5,title),(p.x+MAXIMUM/2-1,p.y-5,"{} | reported GPS offset +{:.2f} m".format(phase.upper(),dx)),(p.x-2,p.y-2,"REAL POSITION"),(p.x+dx+1,p.y-2,"REPORTED GPS" if dx else "GPS MATCHES CAR")]
                for x,y,label in labels:
                    self.world.debug.draw_string(c.Location(x=x,y=y,z=p.z+3),label,draw_shadow=True,color=c.Color(255,255,255),life_time=.18)
            except Exception as exc:
                self.error=str(exc);print("Visualization failed:",exc);return
            self.stop.wait(.10)
    def close(self):
        self.stop.set();self.thread.join(timeout=3)




def record(carla,client,world,car,visuals):
    settings=world.get_settings()
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    folder=Path(__file__).resolve().parent/"results"/("gps_fixed_offset_"+stamp)
    folder.mkdir(parents=True,exist_ok=False)
    p=car.get_location()
    metadata=dict(status="started",started_utc=stamp,map=world.get_map().name,
        client_version=client.get_client_version(),server_version=client.get_server_version(),
        synchronous_mode=settings.synchronous_mode,fixed_delta_seconds=settings.fixed_delta_seconds,
        attack_type="fixed_gps_offset" if MODE=="fixed" else "linear_gps_drift",**SETTINGS,
        offset_direction="CARLA map X, not necessarily east or vehicle forward",sensor_tick_seconds=.1,
        gnss_noise_bias_and_stddev=0.0,scope="GNSS output manipulation only; no driving consumer",
        vehicle_id=car.id,vehicle_start_xyz=[p.x,p.y,p.z],script_version=VERSION,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        visualization="Green real position; red reported position; arrow shows map-X error. Recorded review after live test.")
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
        print("LIVE ATTACK:",TITLE,"| settings (simulation seconds):",SETTINGS)
        print("Results folder:",folder)
        origin=None
        previous=None
        fields=["frame","simulation_time","elapsed_seconds","phase","offset_x_metres",
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
                if elapsed >= DURATION:
                    break
                phase,dx=attack_profile(elapsed)
                actual=data.transform.location
                road_map=world.get_map()
                original=road_map.transform_to_geolocation(actual)
                shifted=road_map.transform_to_geolocation(carla.Location(x=actual.x+dx,y=actual.y,z=actual.z))
                output=(data.latitude+(shifted.latitude-original.latitude),data.longitude+(shifted.longitude-original.longitude),data.altitude)
                writer.writerow([data.frame,data.timestamp,elapsed,phase,dx,
                    actual.x,actual.y,actual.z,data.latitude,data.longitude,data.altitude,*output])
                counts[phase]+=1
                visuals.state=(phase,"LIVE GPS OUTPUT ATTACK | t={:.1f}s".format(elapsed),dx)
                if phase!=previous:
                    print("Phase:",phase,"| simulation elapsed:",round(elapsed,3),"| map-X offset metres:",round(dx,3))
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
    with (folder/"readings.csv").open(newline="") as handle: rows=list(csv.DictReader(handle))
    print("RECORDED REVIEW (not a new attack):",folder.name)
    for phase in PHASES:
        group=[r for r in rows if r["phase"]==phase]
        # Animate drift from actual recorded offsets; retain the final value for screenshots.
        if MODE=="drift" and phase=="drift":
            previous=float(group[0]["elapsed_seconds"])
            for r in group:
                t=float(r["elapsed_seconds"])
                time.sleep(max(0,min(.2,t-previous)))
                visuals.state=(phase,"RECORDED RESULT REPLAY - NOT A LIVE ATTACK",float(r["offset_x_metres"]))
                previous=t
        visuals.state=(phase,"RECORDED RESULT REPLAY - NOT A LIVE ATTACK",float(group[-1]["offset_x_metres"]))
        print("Showing:",phase,"|",len(group),"recorded samples")
        input("Inspect CARLA / take screenshot. Press Enter HERE to continue...")
        if visuals.error: raise RuntimeError(visuals.error)




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
            carla.Location(x=p.x+MAXIMUM/2,y=p.y,z=p.z+25),carla.Rotation(pitch=-90)))
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
