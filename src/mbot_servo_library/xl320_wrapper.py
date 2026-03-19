from dynamixel_sdk import *

# ── Control Table ────────────────────────────────────────────────────────────
BAUDRATE                    = 1000000
PROTOCOL_VERSION            = 2.0

ADDR_ID                     = 3
ADDR_CONTROL_MODE           = 11
ADDR_SHUTDOWN               = 18
ADDR_TORQUE_ENABLE          = 24
ADDR_LED                    = 25
ADDR_GOAL_POSITION          = 30
ADDR_GOAL_SPEED             = 32
ADDR_PRESENT_POSITION       = 37
ADDR_MOVING                 = 49
ADDR_HARDWARE_ERROR_STATUS  = 50

DXL_MINIMUM_POSITION_VALUE  = 0         # Refer to the CW Angle Limit of product eManual
DXL_MAXIMUM_POSITION_VALUE  = 1023      # Refer to the CCW Angle Limit of product eManual

TORQUE_ENABLE               = 1
TORQUE_DISABLE              = 0
WHEEL_MODE                  = 1
JOINT_MODE                  = 2

# LED colors
LED_OFF                     = 0
LED_RED                     = 1
LED_ON                      = 2  # this is green light
LED_YELLOW                  = 3
LED_BLUE                    = 4
LED_PURPLE                  = 5
LED_CYAN                    = 6
LED_WHITE                   = 7
# ─────────────────────────────────────────────────────────────────────────────


class Servo:
    """Control a Dynamixel XL320 servo via GPIO half-duplex UART."""

    def __init__(self, servo_id, portHandler, packetHandler):
        self.servo_id      = servo_id
        self.portHandler   = portHandler
        self.packetHandler = packetHandler

    # ── LED ──────────────────────────────────────────────────────────────────

    def led_switch(self, color):
        """
        @brief Set the LED color. This is an unique feature in XL320.

        @param color  One of the LED_* constants defined in this module
                      (e.g. LED_RED, LED_BLUE).
        """
        result, error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_LED, color)
        self._check(result, error)

    # ── Torque ───────────────────────────────────────────────────────────────

    def enable_torque(self):
        """
        @brief Enable torque.

        Note: must be enabled before moving the servo.
        """
        result, error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Torque enabled")

    def disable_torque(self):
        """
        @brief Disable torque.

        Note: must be disabled before changing control mode.
        """
        result, error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Torque disabled")

    # ── Control Mode ─────────────────────────────────────────────────────────

    def set_control_mode(self, mode):
        """
        @brief Set operating mode.

        @param mode  "wheel" for continuous rotation, "joint" for position control.

        Note: disable torque before calling this.
        """
        if mode not in ("wheel", "joint"):
            print("Control mode must be 'wheel' or 'joint'")
            return
        value = WHEEL_MODE if mode == "wheel" else JOINT_MODE
        result, error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_CONTROL_MODE, value)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Control mode set to {mode}")

    # ── Position (joint mode) ─────────────────────────────────────────────────

    def get_position(self):
        """
        @brief Read present position.

        @return Position in [0, 1023].
        """
        pos, result, error = self.packetHandler.read2ByteTxRx(
            self.portHandler, self.servo_id, ADDR_PRESENT_POSITION)
        if self._check(result, error):
            return pos
        else:
            print(f"[ID:{self.servo_id}] Cannot get position.")
            return None

    def is_moving(self):
        """
        @brief Check if the servo is currently moving.

        @return True if moving, False if goal position reached.
        """
        val, result, error = self.packetHandler.read1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_MOVING)
        self._check(result, error)
        return bool(val)

    def set_position(self, goal_position):
        """
        @brief Set goal position (joint mode).

        @param goal_position  Integer in [0, 1023].
        """
        result, error = self.packetHandler.write2ByteTxRx(
            self.portHandler, self.servo_id, ADDR_GOAL_POSITION, goal_position)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Goal position set to {goal_position}")
        else:
            print(f"[ID:{self.servo_id}] Cannot set position.")

    # ── Speed (joint mode) ───────────────────────────────────────────────────

    def set_joint_speed(self, speed):
        """
        @brief Set movement speed in joint mode.

        @param speed  Integer in [0, 1023]. 0 = maximum speed.
        """
        speed = int(speed)
        if not 0 <= speed <= 1023:
            raise ValueError("Speed must be in [0, 1023]")
        result, error = self.packetHandler.write2ByteTxRx(
            self.portHandler, self.servo_id, ADDR_GOAL_SPEED, speed)
        if self._check(result, error):
            if speed == 0:
                print(f"[ID:{self.servo_id}] Speed set to maximum")
            else:
                print(f"[ID:{self.servo_id}] Speed set to {speed} ({0.111 * speed:.2f} rpm)")

    # ── Speed (wheel mode) ───────────────────────────────────────────────────

    def set_wheel_ccw_speed(self, load):
        """
        @brief Rotate counter-clockwise in wheel mode. This function will convert the percentage to the corresponding speed value that the servo understands. The actual value range is range: 0~1023 and it is stopped by setting to 0.

        @param load  Percentage [0, 100]. 0 = stop.
        """
        load = int(load)
        if not 0 <= load <= 100:
            raise ValueError("Load must be in [0, 100]")
        speed = int(load * 0.01 * 1023)
        result, error = self.packetHandler.write2ByteTxRx(
            self.portHandler, self.servo_id, ADDR_GOAL_SPEED, speed)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Wheel CCW at {load}%")

    def set_wheel_cw_speed(self, load):
        """
        @brief Rotate clockwise in wheel mode. This function convert the percentage to the corresponding speed value that the servo understands. The actual value range is range: 1024~2047 and it is stopped by setting to 1024.

        @param load  Percentage [0, 100]. 0 = stop.
        """
        load = int(load)
        if not 0 <= load <= 100:
            raise ValueError("Load must be in [0, 100]")
        speed = int(load / 100.0 * 1023) + 1024
        result, error = self.packetHandler.write2ByteTxRx(
            self.portHandler, self.servo_id, ADDR_GOAL_SPEED, speed)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Wheel CW at {load}%")

    # ── ID ────────────────────────────────────────────────────────────────────

    def change_id(self, new_id):
        """
        @brief Change the servo's ID and update this instance.

        @param new_id  Integer in [0, 252].

        Note: disable torque before calling this. Power-cycle the servo after.
        """
        result, error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_ID, new_id)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] ID changed to {new_id}")
            self.servo_id = new_id

    # ── Diagnostics ───────────────────────────────────────────────────────────

    def look_error_info(self):
        """@brief Print hardware error status and shutdown info."""
        hw_err, result, error = self.packetHandler.read1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_HARDWARE_ERROR_STATUS)
        print(f"[ID:{self.servo_id}] Hardware Error Status: {hw_err}")

        shutdown, result, error = self.packetHandler.read1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_SHUTDOWN)
        print(f"[ID:{self.servo_id}] Shutdown Error Info:   {shutdown}")

    # ── Internal ──────────────────────────────────────────────────────────────

    def _check(self, result, error):
        """Print SDK errors. Returns True if communication succeeded."""
        if result != COMM_SUCCESS:
            print(self.packetHandler.getTxRxResult(result))
            return False
        if error != 0:
            print(self.packetHandler.getRxPacketError(error))
            return False
        return True
