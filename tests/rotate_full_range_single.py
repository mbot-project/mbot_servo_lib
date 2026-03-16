"""
Servo movement example in "joint" mode (single motor)

This script demonstrates the use of the mbot_servo_library to control a servo motor.
The servo is set to operate in "joint" mode, where it alternates between two goal positions we set.

Use: sudo python3 rotate_full_range_single.py
"""

import time
from mbot_servo_library import *


CONNECTION_DEVICE = "UART"
PORT_NAME = "/dev/ttyAMA0"

# define the servo's ID
servo1_ID = 5

# define Dynamixel moving tolerance
# Don't set it too small such as 1, the servo might never reach the goal.
DXL_MOVING_STATUS_THRESHOLD = 20

def main():
    initialize_GPIO()
    portHandler, packetHandler = initialize_gpio_handlers(PORT_NAME)

    open_port(portHandler)
    set_baudrate(portHandler, 1000000)
    connected_servos = []
    for servo_id in range(20):  # IDs 0-252 are valid
        time.sleep(1)
        model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, servo_id)
        print(f"Trying ID {servo_id}: ", "dxl_comm_result:", dxl_comm_result, "dxl_error:", dxl_error)
        if dxl_comm_result == COMM_SUCCESS:
            connected_servos.append(servo_id)
            print(f"Found servo at ID: {servo_id}")
            break

    # Initialize a Servo instance
    servo1 = Servo(servo1_ID, portHandler, packetHandler)
    servo1.change_led_color(LED_PURPLE)
    servo1.disable_torque()
    servo1.set_control_mode("joint")  # torque must be off when you change mode
    servo1.enable_torque()

    index = 0
    goal_positions = [
        DXL_MINIMUM_POSITION_VALUE,
        DXL_MAXIMUM_POSITION_VALUE,
    ]  # these are the actual limits of the servo

    servo1.set_joint_speed(200)  # range(0,1023)
    time.sleep(1)

    while True:
        print("Press any key to continue! (or press ESC to quit!)")
        if getch() == chr(0x1B):
            break

        servo1.set_position(goal_positions[index])
        time.sleep(1)
        while True:
            servo1_current_position = servo1.get_position()
            time.sleep(1)

            if goal_positions[index] is None or servo1_current_position is None:
                continue

            print("---")
            print("[ID:%d] GoalPos:%d  CurrentPos:%d" % (servo1_ID, goal_positions[index], servo1_current_position))

            if abs(goal_positions[index] - servo1_current_position) <= DXL_MOVING_STATUS_THRESHOLD:
                break

        # Change goal position
        if index == 0:
            index = 1
        else:
            index = 0

    close_port(portHandler)
    close_GPIO()

if __name__ == "__main__":
    main()
