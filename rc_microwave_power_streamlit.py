from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.interpolate import RegularGridInterpolator, interp1d

file_path = Path(__file__).parent


def interpolate_1D(fname: str, path: Path, indices: Sequence[int]) -> interp1d:
    data = np.loadtxt(path / fname, skiprows=1, delimiter=",")

    x, y = data.T[indices]
    return interp1d(x, y)


def interpolate_2D(
    fname: str, path: Path, indices: Sequence[int]
) -> RegularGridInterpolator:
    data = np.loadtxt(path / fname, skiprows=1, delimiter=",")

    x, y, z = data.T[indices]
    _, idx = np.unique(x, return_index=True)
    x = x[np.sort(idx)]
    _, idy = np.unique(y, return_index=True)
    y = y[np.sort(idy)]

    return RegularGridInterpolator((x, y), z.reshape(len(x), len(y)))


"""
Calibrate SynthHD
"""

fname_RFA = "2023_02_13_synthHDPro_SN415_RFA_scan.csv"
fname_RFB = "2023_02_14_synthHDPro_SN415_RFB_scan.csv"

fn_interpolate_SN415_RFA = interpolate_2D(
    fname_RFA, file_path / "measurements SynthHD/data", indices=[0, 1, 2]
)
fn_interpolate_SN415_RFB = interpolate_2D(
    fname_RFB, file_path / "measurements SynthHD/data", indices=[0, 1, 2]
)

fname_RFB = "2023_02_10_synthHDPro_SN416_RFB_scan.csv"
fn_interpolate_SN416_RFB = interpolate_2D(
    fname_RFB, file_path / "measurements SynthHD/data", indices=[0, 1, 2]
)

"""
Calibrate 26.7 GHz
"""

fname = "2023_2_9_synthpower_vg1.csv"

fn_interpolate_26_6GHz_A1 = interpolate_2D(
    fname, file_path / "measurements 26 GHz 2023_2/data", [0, 1, 2]
)
# dBm setpoints from SynthHD Pro SN 416 RFB
setpoints_416 = fn_interpolate_26_6GHz_A1.grid[0]
points = np.vstack([np.ones(len(setpoints_416)) * 13.3e9, setpoints_416]).T
real_power = fn_interpolate_SN416_RFB(points)

grid = list(fn_interpolate_26_6GHz_A1.grid)
grid[0] = real_power
fn_interpolate_26_6GHz_A1.grid = tuple(grid)

fname = "2023_2_9_synthpower_vg2.csv"

fn_interpolate_26_6GHz_A2 = interpolate_2D(
    fname, file_path / "measurements 26 GHz 2023_2/data", [0, 1, 2]
)
# dBm setpoints from SynthHD Pro SN 416 RFB
setpoints_416 = fn_interpolate_26_6GHz_A2.grid[0]
points = np.vstack([np.ones(len(setpoints_416)) * 13.3e9, setpoints_416]).T
real_power = fn_interpolate_SN416_RFB(points)

grid = list(fn_interpolate_26_6GHz_A2.grid)
grid[0] = real_power
fn_interpolate_26_6GHz_A2.grid = tuple(grid)

"""
Calibrate 40 GHz
"""

fname = "2023_2_10_a1_synthd_power.csv"

fn_interpolate_40GHz_A1 = interpolate_1D(
    fname, file_path / "measurements 40 GHz 2023_2/data", indices=[0, 1]
)
# forgot to add 20 dBm to compensate attenuation from directional coupler
fn_interpolate_40GHz_A1.y += 20

# dBm setpoints from SynthHD Pro SN 416 RFB
setpoints_416 = fn_interpolate_40GHz_A1.x
points = np.vstack([np.ones(len(setpoints_416)) * 10e9, setpoints_416]).T
real_power = fn_interpolate_SN416_RFB(points)

fn_interpolate_40GHz_A1.x = real_power

fname = "2023_2_10_a2_synthd_power.csv"

fn_interpolate_40GHz_A2 = interpolate_1D(
    fname, file_path / "measurements 40 GHz 2023_2/data", indices=[0, 1]
)

# forgot to add 20 dBm to compensate attenuation from directional coupler
fn_interpolate_40GHz_A2.y += 20

# dBm setpoints from SynthHD Pro SN 416 RFB
setpoints_416 = fn_interpolate_40GHz_A2.x
points = np.vstack([np.ones(len(setpoints_416)) * 10e9, setpoints_416]).T
real_power = fn_interpolate_SN416_RFB(points)

fn_interpolate_40GHz_A2.x = real_power

calibration_data = dict(
    [
        ("26_7", (fn_interpolate_26_6GHz_A1, fn_interpolate_26_6GHz_A2)),
        ("40", (fn_interpolate_40GHz_A1, fn_interpolate_40GHz_A2)),
        (
            "synthesizers",
            dict(
                [
                    (
                        "SynthHD Pro SN415",
                        (fn_interpolate_SN415_RFA, fn_interpolate_SN415_RFB),
                    ),
                    ("SynthHD Pro SN416", (fn_interpolate_SN416_RFB,)),
                ]
            ),
        ),
    ]
)

st.set_page_config(
    page_title="CeNTREX Rotational Cooling Microwave Power Settings",
    page_icon="📡",
    layout="centered",
)


# with open(file_path / "calibration.pkl", "rb") as f:
#     calibration_data = pickle.load(f)

with st.sidebar:
    synth_select = st.selectbox(
        "Synthesizer", options=["SynthHD Pro SN415", "SynthHD Pro SN416"]
    )
    output_select = st.selectbox("Output", options=["RFA", "RFB"])

    system_select = st.selectbox("System", options=["26.7 GHz", "40 GHz"])

# print(synth_select)
# print(calibration_data["synthesizers"].keys())
ids = 0 if output_select == "RFA" else 1
synthesizer = calibration_data["synthesizers"][synth_select][ids]

if system_select == "26.7 GHz":
    synth_freq = 26.7e9 / 2
    system_calibration = calibration_data["26_7"]
elif system_select == "40 GHz":
    synth_freq = 40e9 / 4
    system_calibration = calibration_data["40"]


setpoints = np.linspace(-30, 5, 501)
points = np.vstack([np.ones(len(setpoints)) * synth_freq, setpoints]).T

real_powers = synthesizer(points)

df = pd.DataFrame(
    dict([("setpoint [dBm]", setpoints), ("measured [dBm]", real_powers)])
)

graph = px.line(
    df,
    x="setpoint [dBm]",
    y="measured [dBm]",
    title=f"Output power of {synth_select} {output_select} @ {synth_freq/1e9:.3f} GHz",
)
st.plotly_chart(graph)


setpoint_select = st.number_input("Power Setpoint [dBm]", -30.0, 5.0, 0.0, step=0.25)
real_power = synthesizer([synth_freq, setpoint_select])[0]
st.write(f"Real output power : {real_power:.1f} dBm")

if system_select == "26.7 GHz":

    col1, col2 = st.columns(2)
    with col1:
        vg_select1 = st.number_input("Vg1 [V]", -1.5, -0.5, -0.7, step=0.01)
        st.write(
            "Amplifier 1:"
            f" {system_calibration[0]([real_power, -vg_select1])[0]:.1f} dBm"
        )
    with col2:
        vg_select2 = st.number_input("Vg2 [V]", -1.5, -0.5, -0.7, step=0.01)
        st.write(
            "Amplifier 2:"
            f" {system_calibration[1]([real_power, -vg_select2])[0]:.1f} dBm"
        )

    real_powers = real_powers[
        real_powers
        > np.max(
            [system_calibration[0].grid[0].min(), system_calibration[1].grid[0].min()]
        )
    ]
    real_powers = real_powers[
        real_powers
        < np.min(
            [system_calibration[0].grid[0].max(), system_calibration[1].grid[0].max()]
        )
    ]

    points = np.vstack([real_powers, np.ones(len(real_powers)) * -vg_select1]).T
    data_vg1 = system_calibration[0](points)
    points = np.vstack([real_powers, np.ones(len(real_powers)) * -vg_select2]).T
    data_vg2 = system_calibration[1](points)

    df = pd.DataFrame(
        dict(
            [
                ("input power [dBm]", real_powers),
                ("Amplifier 1", data_vg1),
                ("Amplifier 2", data_vg2),
            ]
        )
    )

    graph = px.line(
        df,
        x="input power [dBm]",
        y=["Amplifier 1", "Amplifier 2"],
        title=(
            f"Output power {system_select} GHz @ VG1 = {vg_select1:.2f} V, VG2 ="
            f" {vg_select2:.2f} V"
        ),
    )
    graph.add_vline(x=real_power, line_width=2, line_dash="dash")
    graph.update_layout(yaxis_title="output power [dBm]")
    st.plotly_chart(graph)

elif system_select == "40 GHz":

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Amplifier 1: {system_calibration[0](real_power):.1f} dBm")
    with col2:
        st.write(f"Amplifier 2: {system_calibration[1](real_power):.1f} dBm")

    real_powers = real_powers[
        real_powers
        > np.max([system_calibration[0].x.min(), system_calibration[1].x.min()])
    ]
    real_powers = real_powers[
        real_powers
        < np.min([system_calibration[0].x.max(), system_calibration[1].x.max()])
    ]

    data_a1 = system_calibration[0](real_powers)
    data_a2 = system_calibration[1](real_powers)

    df = pd.DataFrame(
        dict(
            [
                ("input power [dBm]", real_powers),
                ("Amplifier 1", data_a1),
                ("Amplifier 2", data_a2),
            ]
        )
    )
    graph = px.line(
        df,
        x="input power [dBm]",
        y=["Amplifier 1", "Amplifier 2"],
        title=f"Output power {system_select} GHz",
    )
    graph.add_vline(x=real_power, line_width=2, line_dash="dash")
    graph.update_layout(yaxis_title="output power [dBm]")
    st.plotly_chart(graph)
