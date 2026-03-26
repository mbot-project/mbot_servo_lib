from dynamixel_sdk import *
from mbot_servo_library import initialize_GPIO, close_GPIO, GPIOPacketHandler
from mbot_servo_library.xseries_wrapper import BAUDRATE
# from mbot_servo_library.xl320_wrapper import BAUDRATE

# define the servo's ID
servo_ID = 1

def main():
    initialize_GPIO()
    portHandler = PortHandler("/dev/ttyAMA0")
    packetHandler = GPIOPacketHandler()

    portHandler.openPort()
    portHandler.setBaudRate(BAUDRATE)

    dxl_comm_result, dxl_error = packetHandler.reboot(portHandler, servo_ID)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    print("[ID:%03d] reboot Succeeded\n" % servo_ID)
    portHandler.closePort()
    close_GPIO()

if __name__ == "__main__":
    main()