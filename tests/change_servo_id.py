"""
Used to change the servo ID.
Duplicate ID will cause communication issues.
Run this script with sudo.
"""

from dynamixel_sdk import *
from mbot_servo_library import *

CURRENT_ID = 1  # The ID you want to change
NEW_ID = 3      # The new ID you want to set

def main():
    initialize_GPIO()
    portHandler, packetHandler = initialize_gpio_handlers("/dev/ttyAMA0")

    open_port(portHandler)
    set_baudrate(portHandler, 1000000)

    servo = Servo(CURRENT_ID, portHandler, packetHandler)
    servo.change_led_color(LED_YELLOW)
    servo.disable_torque()

    print(f"Writing new ID {NEW_ID}...")
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
        portHandler, CURRENT_ID, 3, NEW_ID
    )
    if dxl_comm_result != COMM_SUCCESS:
        print(f"COMM_ERROR: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"DXL_ERROR: {packetHandler.getRxPacketError(dxl_error)}")

    # Ping the servo with the new ID to verify
    model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, NEW_ID)
    print(f"Trying ID {NEW_ID}: ", "dxl_comm_result:", dxl_comm_result, "dxl_error:", dxl_error)
    if dxl_comm_result == COMM_SUCCESS:
        print(f"Found servo at ID: {NEW_ID}")

    close_GPIO()

if __name__ == "__main__":
    main()