"""Connection check previously run successfully on the university PC."""

import carla

client = carla.Client("localhost", 2000)
client.set_timeout(20.0)

print("Client version:", client.get_client_version())
print("Server version:", client.get_server_version())

world = client.get_world()
print("Map:", world.get_map().name)
print("Connection successful")
