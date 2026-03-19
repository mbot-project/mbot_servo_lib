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

Look at definitions in the tests under `lib/DynamixelSDK/python/tests/protocol2_0`, you will see code shown below. Currenly we provide separate wrappers for XL320 and X_SERIES, because they have completely different control table, and seems XL320 is isolated from rest of the family.

```python
#********* DYNAMIXEL Model definition *********
#***** (Use only one definition at a time) *****
MY_DXL = 'X_SERIES'       # X330 (5.0 V recommended), X430, X540, 2X430
# MY_DXL = 'MX_SERIES'    # MX series with 2.0 firmware update.
# MY_DXL = 'PRO_SERIES'   # H54, H42, M54, M42, L54, L42
# MY_DXL = 'PRO_A_SERIES' # PRO series with (A) firmware update.
# MY_DXL = 'P_SERIES'     # PH54, PH42, PM54
# MY_DXL = 'XL320'        # [WARNING] Operating Voltage : 7.4V
```

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