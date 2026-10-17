"""Visual GNSS-output demonstration; no controller or VLA is connected.

CARLA 0.9.14: https://carla.readthedocs.io/en/0.9.14/python_api/
Sensor settings: https://carla.readthedocs.io/en/0.9.14/ref_sensors/#gnss-sensor
"""

import csv
import json
import queue
import time
import threading
from datetime import datetime, timezone
from pathlib import Path

import carla

CLEAN_SECONDS = 5.0
ATTACK_SECONDS = 5.0
OFFSET_X_METRES = 5.0


def main():
    client = carla.Client("localhost", 2000)
    client.set_timeout(20.0)
    world = client.get_world()
    road_map = world.get_map()
    settings = world.get_settings()
    if settings.synchronous_mode:
        raise RuntimeError("World is synchronous. Send this output before changing settings.")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    folder = Path(__file__).resolve().parent / "results" / ("gps_offset_visual_" + stamp)
    folder.mkdir(parents=True, exist_ok=False)
    metadata = {
        "status": "started", "started_utc": stamp, "map": road_map.name,
        "client_version": client.get_client_version(),
        "server_version": client.get_server_version(),
        "synchronous_mode": settings.synchronous_mode,
        "fixed_delta_seconds": settings.fixed_delta_seconds,
        "clean_seconds": CLEAN_SECONDS, "attack_seconds": ATTACK_SECONDS,
        "offset_x_metres": OFFSET_X_METRES, "sensor_tick_seconds": 0.1,
        "gnss_noise_bias_and_stddev": 0.0,
        "scope": "GNSS output manipulation only; no driving consumer",
    }
    vehicle = None
    gps = None
    counts = {"clean": 0, "attack": 0}
    visual_state = [None]
    stop_visual = threading.Event()
    visual_thread = None

    def refresh_visual():
        green = carla.Color(30, 255, 80)
        red = carla.Color(255, 40, 40)
        white = carla.Color(255, 255, 255)
        while not stop_visual.is_set():
            state = visual_state[0]
            if state is not None:
                x, y, z, dx, phase = state
                # Raise markers above the roof for visibility, not as a GPS altitude change.
                real = carla.Location(x=x, y=y, z=z + 1.0)
                reported = carla.Location(x=x + dx, y=y, z=z + 1.0)
                try:
                    world.debug.draw_point(real, size=0.28, color=green, life_time=0.3)
                    world.debug.draw_string(
                        carla.Location(x=x - 1.0, y=y - 1.5, z=z + 1.0),
                        "REAL POSITION", draw_shadow=True, color=green, life_time=0.3)
                    world.debug.draw_string(
                        carla.Location(x=x + 2.5, y=y + 4.0, z=z + 1.0),
                        "CLEAN: GPS MATCHES CAR" if phase == "clean" else "OFFSET ACTIVE: FALSE GPS +5 m",
                        draw_shadow=True, color=white, life_time=0.3)
                    if dx:
                        world.debug.draw_arrow(real, reported, thickness=0.10,
                                               arrow_size=0.35, color=red, life_time=0.3)
                        world.debug.draw_point(reported, size=0.32, color=red, life_time=0.3)
                        world.debug.draw_string(
                            carla.Location(x=x + dx + 0.5, y=y - 1.5, z=z + 1.0),
                            "FALSE GPS POSITION", draw_shadow=True, color=red, life_time=0.3)
                except RuntimeError:
                    return
            stop_visual.wait(0.05)
    try:
        blueprints = world.get_blueprint_library()
        for spawn in road_map.get_spawn_points():
            vehicle = world.try_spawn_actor(blueprints.find("vehicle.tesla.model3"), spawn)
            if vehicle is not None:
                break
        if vehicle is None:
            raise RuntimeError("No available vehicle spawn point.")
        vehicle.apply_control(carla.VehicleControl(brake=1.0, hand_brake=True))
        time.sleep(2.0)
        position = vehicle.get_location()
        metadata["vehicle_id"] = vehicle.id
        metadata["vehicle_start_xyz"] = [position.x, position.y, position.z]
        world.get_spectator().set_transform(carla.Transform(
            carla.Location(x=position.x + OFFSET_X_METRES / 2, y=position.y, z=position.z + 18),
            carla.Rotation(pitch=-90),
        ))

        blueprint = blueprints.find("sensor.other.gnss")
        blueprint.set_attribute("sensor_tick", "0.1")
        for axis in ("lat", "lon", "alt"):
            for parameter in ("bias", "stddev"):
                blueprint.set_attribute("noise_" + axis + "_" + parameter, "0.0")
        gps = world.spawn_actor(blueprint, carla.Transform(carla.Location(z=1.5)),
                                attach_to=vehicle)
        visual_state[0] = (position.x, position.y, position.z + 1.5, 0.0, "clean")
        visual_thread = threading.Thread(target=refresh_visual, daemon=True)
        visual_thread.start()
        print("The car is now visible in CARLA. Green marks its real position.")
        input("Look at CARLA, then press Enter HERE to start the demonstration...")
        samples = queue.Queue()
        gps.listen(samples.put)
        print("Car parked. Recording 5 clean + 5 attacked SIMULATION seconds.")
        print("Results folder:", folder)
        started = None
        previous_phase = None
        deadline = time.monotonic() + 120.0
        fields = ["frame", "simulation_time", "elapsed_seconds", "phase",
                  "offset_x_metres", "sensor_x", "sensor_y", "sensor_z",
                  "clean_latitude", "clean_longitude", "clean_altitude",
                  "reported_latitude", "reported_longitude", "reported_altitude"]
        with (folder / "readings.csv").open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(fields)
            while True:
                if time.monotonic() > deadline:
                    raise RuntimeError("Recording exceeded 120 wall seconds; partial data saved.")
                try:
                    data = samples.get(timeout=10.0)
                except queue.Empty:
                    raise RuntimeError("No GPS sample received for 10 wall seconds.")
                if started is None:
                    started = data.timestamp
                elapsed = data.timestamp - started
                if elapsed >= CLEAN_SECONDS + ATTACK_SECONDS:
                    break
                active = elapsed >= CLEAN_SECONDS
                phase = "attack" if active else "clean"
                dx = OFFSET_X_METRES if active else 0.0
                actual = data.transform.location
                visual_state[0] = (actual.x, actual.y, actual.z, dx, phase)
                original_geo = road_map.transform_to_geolocation(actual)
                shifted_geo = road_map.transform_to_geolocation(carla.Location(
                    x=actual.x + dx, y=actual.y, z=actual.z,
                ))
                # Add the geographic delta to the original measurement.
                # The original CARLA sensor data and the vehicle remain unchanged.
                latitude = data.latitude + (shifted_geo.latitude - original_geo.latitude)
                longitude = data.longitude + (shifted_geo.longitude - original_geo.longitude)
                altitude = data.altitude
                writer.writerow([data.frame, data.timestamp, elapsed, phase, dx,
                                 actual.x, actual.y, actual.z,
                                 data.latitude, data.longitude, data.altitude,
                                 latitude, longitude, altitude])
                counts[phase] += 1
                if phase != previous_phase:
                    print("Phase:", phase, "| elapsed:", round(elapsed, 3), "seconds")
                    print("  Clean lat/lon:", data.latitude, data.longitude)
                    print("  Reported lat/lon:", latitude, longitude)
                    previous_phase = phase
        if not all(counts.values()):
            raise RuntimeError("Both phases must contain samples; inspect partial data.")
        metadata["status"] = "recording_completed"
        print("Recording completed. Sample counts:", counts)
        print("CSV:", folder / "readings.csv")
        if gps.is_listening:
            gps.stop()
        print("No controller/VLA was tested. The parked car should not react.")
        print("CARLA: green = real position; red = false GPS position; arrow = 5 m.")
        print("The car and markers will remain visible for your screenshot or recording.")
        input("Press Enter HERE only when you are finished viewing the result...")
    finally:
        stop_visual.set()
        if visual_thread is not None:
            visual_thread.join(timeout=2.0)
        metadata["sample_counts"] = counts
        metadata["visualization"] = "Green real position; red reported GPS; arrow map-X offset. Markers raised for visibility."
        try:
            if gps is not None:
                if gps.is_listening:
                    gps.stop()
                gps.destroy()
        finally:
            try:
                if vehicle is not None:
                    vehicle.destroy()
            finally:
                (folder / "metadata.json").write_text(json.dumps(metadata, indent=2))
                print("Cleanup attempted. Metadata saved to:", folder / "metadata.json")


if __name__ == "__main__":
    main()
