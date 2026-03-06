"""
Used to check the servo ID.
Loop thru all possible IDs and ping each one.
Run this script with sudo.
"""

from dynamixel_sdk import *
from mbot_servo_library import *

def main():
    initialize_GPIO()
    portHandler, packetHandler = initialize_gpio_handlers("/dev/ttyAMA0")

    open_port(portHandler)
    set_baudrate(portHandler, 1000000)

    # Scan for servos in ID range 0-252
    connected_servos = []
    for servo_id in range(253):  # IDs 0-252 are valid
        model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, servo_id)
        print(f"Trying ID {servo_id}: ", "dxl_comm_result:", dxl_comm_result, "dxl_error:", dxl_error)
        if dxl_comm_result == COMM_SUCCESS:
            connected_servos.append(servo_id)
            print(f"Found servo at ID: {servo_id}")

    print(f"Connected servos: {connected_servos}")

    close_GPIO()

if __name__ == "__main__":
    main()