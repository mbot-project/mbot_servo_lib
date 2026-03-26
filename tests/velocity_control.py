import time, os
from mbot_servo_library import initialize_GPIO, close_GPIO, GPIOPacketHandler
# from mbot_servo_library.xl320_wrapper import *
from mbot_servo_library.xseries_wrapper import *

# define the servo's ID
servo_ID = 1

def getch():
    """
    Gets a single character from standard input.
    This function blocks the program, waits until the user presses a key
    
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
    servo.set_control_mode("velocity")  # torque must be off when you change mode
    servo.enable_torque()

    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1B):
        quit()

    cw = True
    servo.set_wheel_cw_speed(20)
    print("Rotating CW. Press any key to switch direction, ESC to quit.")

    try:
        while True:
            key = getch()
            if key == chr(0x1B):
                servo.set_wheel_cw_speed(0)
                break
            cw = not cw
            if cw:
                servo.set_wheel_cw_speed(20)
                print("Rotating CW. Press any key to switch direction, ESC to quit.")
            else:
                servo.set_wheel_ccw_speed(20)
                print("Rotating CCW. Press any key to switch direction, ESC to quit.")

    except KeyboardInterrupt:
        servo.set_wheel_cw_speed(0)

    finally:
        servo.disable_torque()
        portHandler.closePort()
        close_GPIO()

if __name__ == "__main__":
    main()
