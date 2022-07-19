# Import DroneKit-Python
from dronekit import connect, VehicleMode
import dronekit_sitl

simulator = True

if simulator:
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()
    print(f"Connecting to vehicle on: {connection_string}")
    vehicle = connect(connection_string, wait_ready=True)
else:
    # Serial port on rpi
    connection_string = '/dev/ttyAMA0'
    print(f"Connecting to vehicle on: {connection_string}")
    vehicle = connect(connection_string, wait_ready=True, baud=57600)


while(True):
    try:
        print("[Lat, Long]", vehicle.location.global_frame.lat, vehicle.location.global_frame.lon)
    
    except KeyboardInterrupt:
        vehicle.close()
        if simulator:
            sitl.stop()
        break