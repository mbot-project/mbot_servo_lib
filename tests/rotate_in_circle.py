
"""
Servo movement example in "wheel" mode

This script demonstrates the use of the mbot_servo_library to control servo motors
operating in wheel mode. The servo rotates continuously with a user-defined speed until 
a stop command is issued.

Use: sudo python3 rotate_in_circle.py
"""

from mbot_servo_library import *

CONNECTION_DEVICE = "UART"  
PORT_NAME = "/dev/ttyAMA0" 

# defines the servo's ID
servo1_ID = 2
servo2_ID = 3

def main():
    initialize_GPIO()
    portHandler, packetHandler = initialize_gpio_handlers(PORT_NAME)

    open_port(portHandler)
    set_baudrate(portHandler, 1000000)

    servo1 = Servo(servo1_ID, portHandler, packetHandler)
    servo1.change_led_color(LED_CYAN)
    servo1.disable_torque()
    servo1.set_control_mode("wheel")  # torque must be off when you change mode
    servo1.enable_torque()

    servo2 = Servo(servo2_ID, portHandler, packetHandler)
    servo2.change_led_color(LED_PURPLE)
    servo2.disable_torque()
    servo2.set_control_mode("wheel")  # torque must be off when you change mode
    servo2.enable_torque()

    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1B):
        close_port(portHandler)
        quit()

    servo1.set_wheel_cw_speed(50)  # value is in percentage
    servo2.set_wheel_ccw_speed(30)  # value is in percentage

    try:
        print("Press ESC to stop the servo.")
        while True:  # Start a loop that will run until ESC is pressed
            if getch() == chr(0x1B):
                servo1.set_wheel_cw_speed(0)  # Stop the servo by setting speed to 0
                servo2.set_wheel_ccw_speed(0)  # Stop the servo by setting speed to 0
                break

    except KeyboardInterrupt:
        servo1.set_wheel_cw_speed(0)
        servo2.set_wheel_ccw_speed(0)

    finally:
        servo1.disable_torque()
        servo2.disable_torque()
        close_port(portHandler)
        close_GPIO()


if __name__ == "__main__":
    main()
