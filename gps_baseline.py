import csv
import time
from pathlib import Path

import carla

client = carla.Client("localhost", 2000)
client.set_timeout(20.0)
world = client.get_world()

vehicle = None
gps = None
readings = []
output = Path("gps_baseline.csv").resolve()

try:
    blueprint = world.get_blueprint_library().find("vehicle.tesla.model3")

    for spawn_point in world.get_map().get_spawn_points():
        vehicle = world.try_spawn_actor(blueprint, spawn_point)
        if vehicle is not None:
            break

    if vehicle is None:
        raise RuntimeError("No available vehicle spawn point.")

    vehicle.apply_control(carla.VehicleControl(brake=1.0, hand_brake=True))
    print("Vehicle spawned and parked.")

    time.sleep(2.0)
    position = vehicle.get_location()
    print("Test vehicle ID:", vehicle.id)
    print("Test vehicle position:", position)
    world.get_spectator().set_transform(
        carla.Transform(
            carla.Location(
                x=position.x,
                y=position.y,
                z=position.z + 12
            ),
            carla.Rotation(pitch=-90, yaw=0, roll=0)
        )
    )

    print("Camera moved above the car. Look at the CARLA window.")
    time.sleep(2.0)

    gps_blueprint = world.get_blueprint_library().find("sensor.other.gnss")
    gps_blueprint.set_attribute("sensor_tick", "0.1")

    gps = world.spawn_actor(
        gps_blueprint,
        carla.Transform(carla.Location(z=1.5)),
        attach_to=vehicle,
    )

    def record_gps(data):
        readings.append([
            data.frame,
            data.timestamp,
            data.latitude,
            data.longitude,
            data.altitude,
        ])

    gps.listen(record_gps)

    print("Recording GPS for 10 seconds...")
    time.sleep(10)
    gps.stop()
    print("GPS recording finished. The car is still present.")
    print("Readings collected:", len(readings))
    input("Check the CARLA window. Press Enter here to remove the car...")

finally:
    if gps is not None:
        if gps.is_listening:
            gps.stop()
        gps.destroy()

    if vehicle is not None:
        vehicle.destroy()

    with output.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "frame", "simulation_time",
            "latitude", "longitude", "altitude"
        ])
        writer.writerows(readings)

    print("Readings recorded:", len(readings))
    print("CSV saved to:", output)

    for row in readings[:3]:
        print("Sample:", row)

    if not readings:
        print("No GPS data received. Send this output for diagnosis.")

    print("Test vehicle and sensor removed.")
