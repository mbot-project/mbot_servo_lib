from gpiozero import OutputDevice

PI_CTL_PIN = 18

_ctl_pin = None


def initialize_GPIO():
    """Initialize the GPIO control pin as output, initially LOW."""
    global _ctl_pin
    _ctl_pin = OutputDevice(PI_CTL_PIN, initial_value=False)
    print(f"GPIO pin {PI_CTL_PIN} initialized (LOW)")


def set_pin_high():
    """Set the control pin HIGH (receive mode)."""
    if _ctl_pin:
        _ctl_pin.on()


def set_pin_low():
    """Set the control pin LOW (transmit mode)."""
    if _ctl_pin:
        _ctl_pin.off()


def close_GPIO():
    """Release the GPIO pin."""
    if _ctl_pin:
        _ctl_pin.close()
        print(f"GPIO pin {PI_CTL_PIN} released")
