import time

from SPD3303X import SPD3303X
from utils import check_voltage


def disable_40GHz_power(psu_a_5pos: SPD3303X, dt: float = 2):
    # disable +5V for the SPDT switches
    psu_a_5pos.output(False, 3)

    # disable 12V for the 40 GHz amplifiers
    psu_a_5pos.ch1_voltage_setpoint = 0.0
    psu_a_5pos.ch2_voltage_setpoint = 0.0

    psu_a_5pos.output(False, 1)
    psu_a_5pos.output(False, 2)

    time.sleep(dt)
    assert check_voltage(psu_a_5pos.ch1_voltage, 0.0)
    assert check_voltage(psu_a_5pos.ch2_voltage, 0.0)


if __name__ == "__main__":
    psu_vg_5pos = "USB0::0xF4EC::0x1430::SPD3XIDX5R3677::INSTR"
    psu_12pos_vd_5neg = "USB0::0xF4EC::0x1430::SPD3XIED5R7612::INSTR"
    psu_a_5pos = "USB0::0xF4EC::0x1430::SPD3XIED5R8368::INSTR"

    psu_vg_5pos = SPD3303X(psu_vg_5pos)
    psu_12pos_vd_5neg = SPD3303X(psu_12pos_vd_5neg)
    psu_a_5pos = SPD3303X(psu_a_5pos)

    assert (
        psu_vg_5pos.idn
        == "Siglent Technologies,SPD3303X-E,SPD3XIDX5R3677,1.01.01.02.07R2,V3.0"
    )
    assert (
        psu_12pos_vd_5neg.idn
        == "Siglent Technologies,SPD3303X-E,SPD3XIED5R7612,1.01.01.02.07R2,V3.0"
    )
    assert (
        psu_a_5pos.idn
        == "Siglent Technologies,SPD3303X-E,SPD3XIED5R8368,1.01.01.02.07R2,V3.0"
    )
    disable_40GHz_power(psu_a_5pos)
