
"""
Servo movement example in "wheel" mode

This script demonstrates the use of the mbot_servo_library to control servo motors
operating in wheel mode. The servo rotates continuously with a user-defined speed until 
a stop command is issued.

Use: python3 rotate_in_circle.py
"""

import time, os
from mbot_servo_library import initialize_GPIO, close_GPIO, GPIOPacketHandler
from mbot_servo_library.xl320_wrapper import *

# define the servo's ID
servo_ID = 4

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
    servo.set_control_mode("wheel")  # torque must be off when you change mode
    servo.enable_torque()

    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1B):
        quit()

    servo.set_wheel_cw_speed(20)  # value is in percentage

    try:
        print("Press ESC to stop the servo.")
        while True:  # Start a loop that will run until ESC is pressed
            if getch() == chr(0x1B):
                servo.set_wheel_cw_speed(0)  # Stop the servo by setting speed to 0
                break

    except KeyboardInterrupt:
        servo.set_wheel_cw_speed(0)

    finally:
        servo.disable_torque()
        portHandler.closePort()
        close_GPIO()

if __name__ == "__main__":
    main()
