import csv

import numpy as np
from windfreak import SynthHD

from SPD3303X import SPD3303X
from startup_26GHz import enable_26GHz_power

fname = ""

resource_name_psu_vg = ""
resource_name_psu_2 = ""
resource_name_psu_3 = ""
resource_name_windfreak = ""

psu_vg = SPD3303X(resource_name_psu_vg)
psu_2 = SPD3303X(resource_name_psu_2)
psu_3 = SPD3303X(resource_name_psu_3)

synthhd_pro = SynthHD(resource_name_windfreak)

assert psu_vg.idn == ""
assert psu_2.idn == ""
assert psu_3.idn == ""

with open(fname, "w") as csv_file:
    writer = csv.writer(csv_file)
    # write header
    writer.writerow(["frequency", "power", "vg", "measured power"])

enable_26GHz_power(psu_vg, psu_2, psu_3)

synthhd_pro[0].frequency = 26e9
synthhd_pro[0].power = 0
synthhd_pro[0].enable = True

for vg in np.linspace(1.5, 0.7, 51):
    psu_vg.ch1_voltage_setpoint = vg
    measured_power = 0
    with open(fname, "a") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [synthhd_pro[0].frequency, synthhd_pro[0].power, vg, measured_power]
        )
