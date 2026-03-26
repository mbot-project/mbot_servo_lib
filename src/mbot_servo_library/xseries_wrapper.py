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
ADDR_PROFILE_VELOCITY       = 112   # 4 bytes; speed used in position (joint) mode
ADDR_GOAL_POSITION          = 116   # 4 bytes
ADDR_VELOCITY_LIMIT         = 44    # 4 bytes; caps Goal Velocity and Profile Velocity
ADDR_MOVING                 = 122
ADDR_PRESENT_POSITION       = 132   # 4 bytes

TORQUE_ENABLE               = 1
TORQUE_DISABLE              = 0
VELOCITY_MODE               = 1     # continuous rotation (wheel equivalent)
POSITION_MODE               = 3     # position control    (joint equivalent)
EXTENDED_POSITION_MODE      = 4     # multi-turn position; counts linearly (-256 to +256 rev, i.e. -1,048,576 to 1,048,576 counts)

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
        vel_limit, result, error = self.packetHandler.read4ByteTxRx(
            self.portHandler, self.servo_id, ADDR_VELOCITY_LIMIT)
        self.vel_limit = vel_limit if result == COMM_SUCCESS else 200

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

        @param mode  "velocity" for velocity/continuous rotation,
                     "position" for position control.
                     "extended_position" for exteneded beyond 360 degrees

        Note: disable torque before calling this.
        """
        if mode not in ("position", "velocity", "extended_position"):
            print("Control mode must be 'position', 'extended_position` or 'velocity'")
            return
        if mode == "velocity":
            value = VELOCITY_MODE
        elif mode == "extended_position":
            value = EXTENDED_POSITION_MODE
        else:
            value = POSITION_MODE
        result, error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.servo_id, ADDR_OPERATING_MODE, value)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Control mode set to {mode}")

    # ── Position (joint mode) ─────────────────────────────────────────────────

    def get_position(self):
        """
        @brief Read present position.

        @return Position in [0, 4095] in position mode.
                In extended position mode, a linear count that keeps
                accumulating across full rotations: range is roughly
                -1,048,576 to 1,048,576 (-256 to +256 revolutions at
                4096 counts/rev).
        """
        pos, result, error = self.packetHandler.read4ByteTxRx(
            self.portHandler, self.servo_id, ADDR_PRESENT_POSITION)
        self._check(result, error)
        if pos > 0x7FFFFFFF:   # convert unsigned 32-bit to signed
            pos -= 0x100000000
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
        @brief Set goal position.

        @param goal_position  In position mode: integer in [0, 4095].
                              In extended position mode: linear count that
                              accumulates across rotations; range is roughly
                              -1,048,576 to 1,048,576 (-256 to +256 revolutions
                              at 4096 counts/rev). Min/Max Position Limit
                              registers are ignored in this mode.
        """
        result, error = self.packetHandler.write4ByteTxRx(
            self.portHandler, self.servo_id, ADDR_GOAL_POSITION, goal_position)
        if self._check(result, error):
            print(f"[ID:{self.servo_id}] Goal position set to {goal_position}")

    # ── Speed (position control mode) ───────────────────────────────────────

    def set_pos_ctl_speed(self, speed):
        """
        @brief Set profile velocity used when moving to a goal position.

        @param speed  Integer in [0, 32737]. 0 = maximum speed.
                      Unit: 0.229 rpm per count.

        @note for XL330, if speed higher than 500, it might trigger time-out
        """
        speed = int(speed)
        if not (0 <= speed <= 500):
            print("[Warning] If you are using XL330, speed > 500 might trigger hardware error.")
        result, error = self.packetHandler.write4ByteTxRx(
            self.portHandler, self.servo_id, ADDR_PROFILE_VELOCITY, speed)
        if self._check(result, error):
            if speed == 0:
                print(f"[ID:{self.servo_id}] Speed set to maximum.")
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
        speed = int(load / 100.0 * self.vel_limit)  # positive → CCW
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
        speed = -int(load / 100.0 * self.vel_limit) # negative → CW
        result, error = self.packetHandler.write4ByteTxRx(
            self.portHandler, self.servo_id, ADDR_GOAL_VELOCITY, speed)
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
