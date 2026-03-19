"""
Servo movement example in "joint" mode (single motor)

This script demonstrates the use of the mbot_servo_library to control a servo motor.
The servo is set to operate in "joint" mode, where it alternates between two goal positions we set.

Use: python3 rotate_full_range_single.py
"""

import time, os
from mbot_servo_library import initialize_GPIO, close_GPIO, GPIOPacketHandler
# from mbot_servo_library.xl320_wrapper import *
from mbot_servo_library.xseries_wrapper import *

# define the servo's ID
servo_ID = 1

def getch():
    """
    Gets a single character from standard input.

    @return: The character pressed by the user.
    """
    if os.name == "nt":
        import msvcrt

        return msvcrt.getch().decode()
    else:
        import tty, termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def main():
    initialize_GPIO()
    portHandler = PortHandler("/dev/ttyAMA0")
    packetHandler = GPIOPacketHandler()

    portHandler.openPort()
    portHandler.setBaudRate(BAUDRATE)
    time.sleep(1)

    # Initialize a Servo instance
    servo = Servo(servo_ID, portHandler, packetHandler)
    servo.led_switch(LED_ON)
    servo.disable_torque()
    servo.set_control_mode("joint")  # torque must be off when you change mode
    servo.enable_torque()

    servo.set_joint_speed(200)  # range(0,1023)
    goal_positions = [40,1000]   # range(0,1023)

    for goal_position in goal_positions:
        print("Press any key to continue! (or press ESC to quit!)")
        if getch() == chr(0x1B):
            close_port(portHandler)
            quit()
        servo.set_position(goal_position)
        while 1:
            time.sleep(0.1)
            servo_current_position = servo.get_position()
            if servo_current_position:
                print("[ID:%d] GoalPos:%d  CurrentPos:%d" % (servo_ID, goal_position, servo_current_position))
                if abs(goal_position - servo_current_position) <= 10:
                    break
            else:
                break

    portHandler.closePort()
    close_GPIO()

if __name__ == "__main__":
    main()
