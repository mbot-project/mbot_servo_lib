# MBOT Servo Library

This is a Python library for Dynamixel servos (XL320, XL330, and more) using DynamixelSDK.

This is for Botlab in ROB 550 use on ROS MBot, and is different from the Jetson Nano and armlab servo libraries.

This is compatible with Pi5 and only tested on Pi5.


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
1. Check the servo ID. This program will ping all the possible IDs and give you the list of connected IDs. Connect one servo to Pi at a time for ID checking.
    ```bash
    cd ~/mbot_servo_lib/tests
    sudo python3 check_servo_id.py
    ```
2. Avoid using an identical ID for multiple servos. You may face communication failure or may not be able to detect a servo with an identical ID - [Source](https://emanual.robotis.com/docs/en/dxl/x/xl320/#id). Modify `change_servo_id.py` to change the ID.
    ```bash
    sudo python3 change_servo_id.py
    ```
3. We have 2 examples `tests/rotate_full_range.py` and `tests/rotate_in_circle.py`. You need to define the servo ID to use the 2 examples, and the IDs are the ones you obtain from step 1.
    ```python3
    # defines the servo's ID
    servo1_ID = 1
    servo2_ID = 2
    ```
    ```bash
    sudo python3 rotate_in_circle.py
    ```
## Uninstall
```bash
sudo pip3 uninstall dynamixel_sdk mbot_servo_library --break-system-packages
```
## A few things
1. gpiod: Uses the native BCM (or GPIO) numbers. Unlike Jetson.GPIO (with GPIO.BOARD): Uses the physical pin numbers on the header.