from dynamixel_sdk import *

# ── Control Table (X-Series: XL330, XC330, XM430, XH430, XH540 …) ────────────
BAUDRATE                    = 57600
PROTOCOL_VERSION            = 2.0

ADDR_ID                     = 7
ADDR_OPERATING_MODE         = 11
ADDR_SHUTDOWN               = 63
ADDR_TORQUE_ENABLE          = 64
ADDR_LED                    = 65
ADDR_HARDWARE_ERROR_STATUS  = 70
ADDR_GOAL_VELOCITY          = 104   # 4 bytes, signed; used in velocity (wheel) mode
ADDR_PROFILE_VELOCITY       = 112   # 4 bytes; max speed used in position (joint) mode
ADDR_GOAL_POSITION          = 116   # 4 bytes
ADDR_MOVING                 = 122
ADDR_PRESENT_POSITION       = 132   # 4 bytes

DXL_MINIMUM_POSITION_VALUE  = 0     # Refer to the Minimum Position Limit of product eManual
DXL_MAXIMUM_POSITION_VALUE  = 4095  # Refer to the Maximum Position Limit of product eManual

TORQUE_ENABLE               = 1
TORQUE_DISABLE              = 0
VELOCITY_MODE               = 1     # continuous rotation (wheel equivalent)
POSITION_MODE               = 3     # position control    (joint equivalent)

# LED: X-series has a single LED, not color
LED_OFF                     = 0
LED_ON                      = 1
# ─────────────────────────────────────────────────────────────────────────────


class Servo:
    """Control a Dynamixel X-Series servo via GPIO half-duplex UART.

    Covers XL330, XC330, XM430, XH430, XH540, and other X-series models
    that share the same control table.
    """

    def __init__(self, servo_id, portHandler, packetHandler):
        self.servo_id      = servo_id
        self.portHandler   = portHandler
        self.packetHandler = packetHandler

    # ── LED ──────────────────────────────────────────────────────────────────

    def led_switch(self, switch):
        """
        @brief Turn the LED on or off.

        @param switch LED_ON (1) or LED_OFF (0).
        """
        result, error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_LED, switch)
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

        Note: must be disabled before changing operating mode.
        """
        result, error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Torque disabled")

    # ── Operating Mode ───────────────────────────────────────────────────────

    def set_control_mode(self, mode):
        """
        @brief Set operating mode.

        @param mode  "wheel" for velocity/continuous rotation,
                     "joint" for position control.

        Note: disable torque before calling this.
        """
        if mode not in ("wheel", "joint"):
            print("Control mode must be 'wheel' or 'joint'")
            return
        value = VELOCITY_MODE if mode == "wheel" else POSITION_MODE
        result, error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_OPERATING_MODE, value)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Control mode set to {mode}")

    # ── Position (joint mode) ─────────────────────────────────────────────────

    def get_position(self):
        """
        @brief Read present position.

        @return Position in [0, 4095].
        """
        pos, result, error = self.packetHandler.read4ByteTxRx(
            self.portHandler, self.servo_id, ADDR_PRESENT_POSITION)
        self._check(result, error)
        return pos

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

        @param goal_position  Integer in [0, 4095].
        """
        result, error = self.packetHandler.write4ByteTxRx(
            self.portHandler, self.servo_id, ADDR_GOAL_POSITION, goal_position)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Goal position set to {goal_position}")

    # ── Speed (joint mode) ───────────────────────────────────────────────────

    def set_joint_speed(self, speed):
        """
        @brief Set profile velocity used when moving to a goal position.

        @param speed  Integer in [0, 1023]. 0 = maximum speed.
                      Unit: 0.229 rpm per count.
        """
        speed = int(speed)
        if not 0 <= speed <= 1023:
            raise ValueError("Speed must be in [0, 1023]")
        result, error = self.packetHandler.write4ByteTxRx(
            self.portHandler, self.servo_id, ADDR_PROFILE_VELOCITY, speed)
        if self._check(result, error):
            if speed == 0:
                print(f"[ID:{self.servo_id}] Speed set to maximum")
            else:
                print(f"[ID:{self.servo_id}] Speed set to {speed} ({0.229 * speed:.2f} rpm)")

    # ── Speed (wheel / velocity mode) ────────────────────────────────────────

    def set_wheel_ccw_speed(self, load):
        """
        @brief Rotate counter-clockwise in wheel mode.

        @param load  Percentage [0, 100]. 0 = stop.

        Goal Velocity is a signed 4-byte value; positive = CCW.
        """
        load = int(load)
        if not 0 <= load <= 100:
            raise ValueError("Load must be in [0, 100]")
        speed = int(load / 100.0 * 1023)          # positive → CCW
        result, error = self.packetHandler.write4ByteTxRx(
            self.portHandler, self.servo_id, ADDR_GOAL_VELOCITY, speed)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Wheel CCW at {load}%")

    def set_wheel_cw_speed(self, load):
        """
        @brief Rotate clockwise in wheel mode.

        @param load  Percentage [0, 100]. 0 = stop.

        Goal Velocity is a signed 4-byte value; negative = CW.
        """
        load = int(load)
        if not 0 <= load <= 100:
            raise ValueError("Load must be in [0, 100]")
        speed = -int(load / 100.0 * 1023)         # negative → CW
        speed_raw = speed & 0xFFFFFFFF             # two's complement for SDK
        result, error = self.packetHandler.write4ByteTxRx(
            self.portHandler, self.servo_id, ADDR_GOAL_VELOCITY, speed_raw)
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
