"""
Used to check the servo ID.
Loop thru all possible IDs and ping each one.
"""

from dynamixel_sdk import *
from mbot_servo_library import initialize_GPIO, close_GPIO, GPIOPacketHandler
# from mbot_servo_library.xseries_wrapper import BAUDRATE
from mbot_servo_library.xl320_wrapper import BAUDRATE

def main():
    initialize_GPIO()
    portHandler = PortHandler("/dev/ttyAMA0")
    packetHandler = GPIOPacketHandler()

    portHandler.openPort()
    portHandler.setBaudRate(BAUDRATE)

    # Scan for servos in ID range 0-252
    connected_servos = []
    for servo_id in range(20):  # IDs 0-252 are valid
        time.sleep(0.05)
        model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, servo_id)
        print(f"Trying ID {servo_id}: ", "dxl_comm_result:", dxl_comm_result, "dxl_error:", dxl_error)
        if dxl_comm_result == COMM_SUCCESS:
            connected_servos.append(servo_id)
            print(f"Found servo at ID: {servo_id}")
            break

    print(f"Connected servos: {connected_servos}")

    portHandler.closePort()
    close_GPIO()

if __name__ == "__main__":
    main()