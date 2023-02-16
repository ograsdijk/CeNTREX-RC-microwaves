import pickle

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="CeNTREX Rotational Cooling Microwave Power Settings",
    page_icon="📡",
    layout="centered",
)

with open("calibration.pkl", "rb") as f:
    calibration_data = pickle.load(f)

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
