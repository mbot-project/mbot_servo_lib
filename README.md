# MBOT Servo Library

This is a Python library for Dynamixel servos using DynamixelSDK.

This is compatible with Pi5 and only tested on Pi5. Curerntly tested with XL320, XL330-M288, XL430-W250.

## Install
1. Edit the Configuration File.
    ```bash
    sudo nano /boot/firmware/config.txt
    ```
2. Add UART Overlay: Add the following lines to the end of the file to enable the primary UART on GPIO pins 14 (TX) and 15 (RX) :
    ```bash
    [pi5]
    dtoverlay=uart0-pi5
    ```
3. Run the following to add user to dialout group:
    ```bash
    sudo usermod -a -G dialout $USER
    ```
4. Reboot your Raspberry Pi for the changes to take effect.
    ```bash
    sudo reboot
    ```
5. Test. Run the following command we should see `ttyAMA0` list
    ```
    $ ls /dev | grep ttyAMA
    ttyAMA0
    ttyAMA10
    ```
    Then run `groups` and you should see `dialout` listed.
6. Run the following install script
    ```bash
    cd ~/mbot_servo_lib
    ./install.sh
    ```
    - After installing the library, any script, anywhere, can do `from mbot_servo_library import *`

You are all set.

## How to use

```bash
from mbot_servo_library.xseries_wrapper import BAUDRATE, Servo
# from mbot_servo_library.xl320_wrapper import BAUDRATE, Servo
```
- If you are using XL320, which is very unstable, you need to switch from xseries_wrapper to xl320_wrapper, they have different control table.
- If you are using XL330-M288 or XL430-W250, proceed.


1. Check the servo ID. This program will ping all the possible IDs and give you the list of connected IDs. Connect one servo to Pi at a time for ID checking.
    ```bash
    cd ~/mbot_servo_lib/tests
    python3 check_servo_id.py
    ```
2. Modify `change_servo_id.py` to change the ID if you use more than 1 servo, we need to avoid using identical ID for multiple servos. You may face communication failure or may not be able to detect a servo with an identical ID - [Source](https://emanual.robotis.com/docs/en/dxl/x/xl320/#id). 
    ```bash
    python3 change_servo_id.py
    ```
3. We have 3 examples `tests/position_control.py`, `tests/extended_position_control.py`, and `tests/velocity_control.py`. You need to define the servo ID to use them, and the ID is the one you obtain from step 1.
    ```bash
    python3 velocity_control.py
    ```
## Uninstall
```bash
sudo pip3 uninstall dynamixel_sdk mbot_servo_library --break-system-packages
```
## A few things
1. gpiod: Uses the native BCM (or GPIO) numbers. Unlike Jetson.GPIO (with GPIO.BOARD): Uses the physical pin numbers on the header.