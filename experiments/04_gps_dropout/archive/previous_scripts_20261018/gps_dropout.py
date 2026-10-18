"""GPS output dropout with visual status; no controller or VLA is connected.

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
DROPOUT_SECONDS = 5.0
RECOVERY_SECONDS = 5.0


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


def main():
    client = carla.Client("localhost", 2000)
    client.set_timeout(20.0)
    world = client.get_world()
    road_map = world.get_map()
    settings = world.get_settings()
    if settings.synchronous_mode:
        raise RuntimeError("World is synchronous. Send this output before changing settings.")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    folder = Path(__file__).resolve().parent / "results" / ("gps_dropout_" + stamp)
    folder.mkdir(parents=True, exist_ok=False)
    metadata = {
        "status": "started", "started_utc": stamp, "map": road_map.name,
        "client_version": client.get_client_version(),
        "server_version": client.get_server_version(),
        "synchronous_mode": settings.synchronous_mode,
        "fixed_delta_seconds": settings.fixed_delta_seconds,
        "attack_type": "gps_output_dropout",
        "clean_seconds": CLEAN_SECONDS, "dropout_seconds": DROPOUT_SECONDS,
        "recovery_seconds": RECOVERY_SECONDS,
        "dropout_representation": "output_available=false; reported coordinates empty",
        "recovery_policy": "pass the current sample; no stale replay",
        "sensor_tick_seconds": 0.1,
        "gnss_noise_bias_and_stddev": 0.0,
        "scope": "GNSS output manipulation only; no driving consumer",
    }
    vehicle = None
    gps = None
    counts = {"clean": 0, "dropout": 0, "recovery": 0}
    visual_state = [None]
    stop_visual = threading.Event()
    visual_thread = None

    def refresh_visual():
        green = carla.Color(30, 200, 65)
        red = carla.Color(220, 40, 35)
        white = carla.Color(255, 255, 255)
        while not stop_visual.is_set():
            state = visual_state[0]
            if state is not None:
                x, y, z, available, phase, elapsed = state
                status = {"ready": "READY - PRESS ENTER IN TERMINAL",
                          "clean": "GPS AVAILABLE",
                          "dropout": "GPS UNAVAILABLE - OUTPUT WITHHELD",
                          "recovery": "GPS RESTORED - CURRENT READINGS",
                          "completed": "COMPLETE - GPS RECOVERY RECORDED"}[phase]
                color = green if available else red
                try:
                    # This is ground truth, NOT a reported GPS coordinate.
                    world.debug.draw_string(
                        carla.Location(x=x - 2, y=y - 2, z=z + 1),
                        "REAL CAR (GROUND TRUTH)", draw_shadow=True,
                        color=white, life_time=0.12)
                    world.debug.draw_string(
                        carla.Location(x=x + 5, y=y - 5, z=z + 1),
                        status, draw_shadow=True, color=color, life_time=0.12)
                    world.debug.draw_string(
                        carla.Location(x=x + 4, y=y - 5, z=z + 1),
                        "5s NORMAL | 5s NO OUTPUT | 5s RECOVERY",
                        draw_shadow=True, color=white, life_time=0.12)
                    world.debug.draw_string(
                        carla.Location(x=x + 3, y=y - 5, z=z + 1),
                        "t={:.1f}s | PARKED CAR - NO CONTROLLER/VLA".format(elapsed),
                        draw_shadow=True, color=white, life_time=0.12)
                    if available:
                        world.debug.draw_point(carla.Location(x=x, y=y, z=z+1),
                                               size=0.14, color=green, life_time=0.12)
                    # No GPS position marker is drawn while output is missing.
                except RuntimeError:
                    return
            stop_visual.wait(0.10)
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
            carla.Location(x=position.x + 2, y=position.y, z=position.z + 22),
            carla.Rotation(pitch=-90),
        ))

        blueprint = blueprints.find("sensor.other.gnss")
        blueprint.set_attribute("sensor_tick", "0.1")
        for axis in ("lat", "lon", "alt"):
            for parameter in ("bias", "stddev"):
                blueprint.set_attribute("noise_" + axis + "_" + parameter, "0.0")
        gps = world.spawn_actor(blueprint, carla.Transform(carla.Location(z=1.5)),
                                attach_to=vehicle)
        visual_state[0] = (position.x, position.y, position.z + 1.5, True, "ready", 0.0)
        visual_thread = threading.Thread(target=refresh_visual, daemon=True)
        visual_thread.start()
        print("Vehicle spawned; view positioned above it. Status labels show reported GPS availability.")
        input("Look at CARLA, then press Enter HERE to start the demonstration...")
        samples = queue.Queue()
        gps.listen(samples.put)
        print("Car parked. Recording 5 clean + 5 dropout + 5 recovery SIMULATION seconds.")
        print("Results folder:", folder)
        started = None
        previous_phase = None
        last_print_second = None
        deadline = time.monotonic() + 120.0
        fields = ["frame", "simulation_time", "elapsed_seconds", "phase",
                  "output_available", "sensor_x", "sensor_y", "sensor_z",
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
                if elapsed >= CLEAN_SECONDS + DROPOUT_SECONDS + RECOVERY_SECONDS:
                    break
                phase, available = attack_profile(elapsed)
                actual = data.transform.location
                visual_state[0] = (actual.x, actual.y, actual.z, available, phase, elapsed)
                latitude, longitude, altitude = reported_output(
                    data.latitude, data.longitude, data.altitude, available)
                writer.writerow([data.frame, data.timestamp, elapsed, phase, int(available),
                                 actual.x, actual.y, actual.z,
                                 data.latitude, data.longitude, data.altitude,
                                 latitude, longitude, altitude])
                counts[phase] += 1
                second = int(elapsed)
                if second != last_print_second:
                    print("t={:.1f}s | phase={} | reported GPS available={}".format(
                        elapsed, phase, available))
                    last_print_second = second
                if phase != previous_phase:
                    print("Phase:", phase, "| elapsed:", round(elapsed, 3), "seconds")
                    print("  Clean lat/lon:", data.latitude, data.longitude)
                    print("  Reported lat/lon:", latitude, longitude)
                    previous_phase = phase
        if not all(counts.values()):
            raise RuntimeError("All three phases must contain samples; inspect partial data.")
        metadata["status"] = "recording_completed"
        metadata["sample_counts"] = counts
        (folder / "metadata.json").write_text(json.dumps(metadata, indent=2))
        print("Recording completed. Sample counts:", counts)
        print("CSV:", folder / "readings.csv")
        if gps.is_listening:
            gps.stop()
        print("No controller/VLA was tested. The parked car should not react.")
        visual_state[0] = (actual.x, actual.y, actual.z, True, "completed", elapsed)
        print("Dropout rows contain raw GPS but EMPTY reported coordinates, not zeros.")
        print("During dropout: red status label, no reported GPS marker.")
        print("The car and markers will remain visible for your screenshot or recording.")
        input("Press Enter HERE only when you are finished viewing the result...")
    except BaseException as exc:
        if metadata["status"] != "recording_completed":
            metadata["status"] = "interrupted" if isinstance(exc, (KeyboardInterrupt, EOFError)) else "failed"
            metadata["error"] = str(exc)
        raise
    finally:
        stop_visual.set()
        if visual_thread is not None:
            visual_thread.join(timeout=2.0)
        metadata["sample_counts"] = counts
        metadata["visualization"] = "Ground-truth car label always shown; GPS output marker only when available; status labels show clean/dropout/recovery. No false GPS position is drawn."
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
