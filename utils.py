import numpy as np


def check_voltage(voltage: float, setpoint: float, tolerance: float = 0.02) -> bool:
    if setpoint == 0:
        return setpoint == voltage
    else:
        return abs(voltage - setpoint) < tolerance * voltage


def watt_to_dBm(watt: float) -> float:
    return 10 * np.log10(watt * 1e3)
