# Import DroneKit-Python
from dronekit import connect, VehicleMode
import dronekit_sitl
import time

simulator = False

if simulator:
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()
    vehicle = connect(connection_string, wait_ready=True)
else:
    # Serial port on rpi
    connection_string = '/dev/ttyAMA0'
    vehicle = connect(connection_string, wait_ready=True, baud=57600)

fileName = "gps_log.txt"

with open(fileName, "w") as file:
    for i in range(100):
        try:
            # log = f"[GPS Coordinates]: {vehicle.location.global_frame.lat}, {vehicle.location.global_frame.lon} \n"
            # file.write(log)
            print(vehicle.battery)
        except KeyboardInterrupt:
            vehicle.close()
            if simulator:
                sitl.stop()
            break