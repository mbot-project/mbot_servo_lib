"""
Used to change the servo ID.
Duplicate ID will cause communication issues.
Run this script with sudo.
"""

from dynamixel_sdk import *
from mbot_servo_library import initialize_GPIO, close_GPIO, GPIOPacketHandler
from mbot_servo_library.xseries_wrapper import BAUDRATE, Servo
# from mbot_servo_library.xl320_wrapper import BAUDRATE, Servo

CURRENT_ID = 3  # The ID you want to change
NEW_ID = 2      # The new ID you want to set

def main():
    initialize_GPIO()
    portHandler = PortHandler("/dev/ttyAMA0")
    packetHandler = GPIOPacketHandler()

    portHandler.openPort()
    portHandler.setBaudRate(BAUDRATE)

    servo = Servo(CURRENT_ID, portHandler, packetHandler)

    print(f"Writing new ID {NEW_ID}...")
    servo.change_id(NEW_ID)

    # Ping the servo with the new ID to verify
    model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, NEW_ID)
    print(f"Trying ID {NEW_ID}: ", "dxl_comm_result:", dxl_comm_result, "dxl_error:", dxl_error)
    if dxl_comm_result == COMM_SUCCESS:
        print(f"Found servo at ID: {NEW_ID}")

    portHandler.closePort()
    close_GPIO()

if __name__ == "__main__":
    main()