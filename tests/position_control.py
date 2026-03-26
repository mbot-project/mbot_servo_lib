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
    servo.set_control_mode("position")  # torque must be off when you change mode
    servo.enable_torque()

    servo.set_pos_ctl_speed(200)  # range [0, 32737], 0 is max
    goal_positions = [10, 4090, 10]   # range [0, 4095]

    for goal_position in goal_positions:
        print("Press any key to continue! (or press ESC to quit!)")
        if getch() == chr(0x1B):
            portHandler.closePort()
            quit()
        servo.set_position(goal_position)
        while 1:
            time.sleep(0.1)
            servo_current_position = servo.get_position()
            if servo_current_position:
                print("[ID:%d] GoalPos:%d  CurrentPos:%d" % (servo_ID, goal_position, servo_current_position))
                if abs(goal_position - servo_current_position) <= 20:
                    break
            else:
                break

    portHandler.closePort()
    close_GPIO()

if __name__ == "__main__":
    main()
