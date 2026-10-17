"""Earlier diagnostic: find the test Tesla and move the viewing camera.

This changes the spectator view only when exactly one Tesla Model 3 exists.
Run while the baseline script is waiting with its vehicle still present.
"""

import carla

client = carla.Client("localhost", 2000)
client.set_timeout(20.0)
world = client.get_world()

vehicles = list(world.get_actors().filter("vehicle.tesla.model3"))
print("Tesla vehicles found:", len(vehicles))

for vehicle in vehicles:
    print("Vehicle ID:", vehicle.id)
    print("Current position:", vehicle.get_location())

if len(vehicles) == 1:
    vehicle = vehicles[0]
    transform = vehicle.get_transform()
    forward = transform.get_forward_vector()

    camera_position = carla.Location(
        x=transform.location.x - forward.x * 8,
        y=transform.location.y - forward.y * 8,
        z=transform.location.z + 4,
    )

    world.get_spectator().set_transform(
        carla.Transform(
            camera_position,
            carla.Rotation(pitch=-25, yaw=transform.rotation.yaw)
        )
    )
    print("Camera positioned behind the vehicle.")
else:
    print("Camera unchanged: send this output so we can identify the test car.")
