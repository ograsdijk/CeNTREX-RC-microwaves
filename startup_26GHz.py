import time

from SPD3303X import SPD3303X
from utils import check_voltage


def enable_26GHz_power(
    psu_vg_5pos: SPD3303X, psu_12pos_vd_5neg: SPD3303X, dt: float = 2
):
    # enable 12V fans, doubling stage
    psu_12pos_vd_5neg.ch1_voltage_setpoint = 12
    psu_12pos_vd_5neg.ch1_current_setpoint = 3.0
    psu_12pos_vd_5neg.output(True, 1)
    time.sleep(dt)
    assert check_voltage(psu_12pos_vd_5neg.ch1_voltage, 12.0)

    # enable +/- 5V for the SPDT switches
    psu_vg_5pos.output(True, 3)
    psu_12pos_vd_5neg.output(True, 3)

    # enable amplifiers
    # first set the gate voltage to -1.5V
    psu_vg_5pos.ch1_voltage_setpoint = 1.5
    psu_vg_5pos.ch1_current_setpoint = 0.07

    psu_vg_5pos.ch2_voltage_setpoint = 1.5
    psu_vg_5pos.ch2_current_setpoint = 0.07

    psu_vg_5pos.output(True, 1)
    psu_vg_5pos.output(True, 2)
    time.sleep(dt)
    assert check_voltage(psu_vg_5pos.ch1_voltage, 1.5)
    assert check_voltage(psu_vg_5pos.ch2_voltage, 1.5)

    # turn on the VD = +6V PSU
    psu_12pos_vd_5neg.ch2_voltage_setpoint = 6.0
    psu_12pos_vd_5neg.ch2_current_setpoint = 3.2

    psu_12pos_vd_5neg.output(True, 2)
    time.sleep(dt)
    assert check_voltage(psu_12pos_vd_5neg.ch2_voltage, 6.0)

    # tune gate voltage for appropriate amplification
    psu_vg_5pos.ch1_voltage_setpoint = 0.8
    psu_vg_5pos.ch2_voltage_setpoint = 0.8
    time.sleep(dt)
    assert check_voltage(psu_vg_5pos.ch1_voltage, 0.8)
    assert check_voltage(psu_vg_5pos.ch2_voltage, 0.8)


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
    enable_26GHz_power(psu_vg_5pos, psu_12pos_vd_5neg)
