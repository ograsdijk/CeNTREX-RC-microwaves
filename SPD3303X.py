import pyvisa


class SPD3303X:
    def __init__(self, resource: str):
        self.rm = pyvisa.ResourceManager()
        self.dev = self.rm.open_resource(resource_name=resource)
        self.dev.read_termination = "\n"

    def _query(self, command: str) -> str:
        return self.dev.query(command)

    def _write(self, command: str):
        self.dev.write(command)

    @property
    def idn(self):
        return self._query("*IDN?")

    def save(self, memory: int):
        self._write(f"*SAV{memory}")

    def voltage_setpoint(self, voltage: float, channel: int):
        self._write(f"CH{channel}:VOLT {voltage}")

    def current_setpoint(self, current: float, channel: int):
        self._write(f"CH{channel}:CURR {current}")

    def power(self, channel: int) -> float:
        return float(self._query(f"MEAS:POWE? CH{channel}"))

    def output(self, on: bool, channel: int):
        if on:
            state = "ON"
        else:
            state = "OFF"
        self._write(f"OUTP CH{channel},{state}")

    @property
    def ch1_power(self) -> float:
        return self.power(1)

    @property
    def ch1_voltage(self) -> float:
        return float(self._query("MEAS:VOLT? CH1"))

    @property
    def ch1_current(self) -> float:
        return float(self._query("MEAS:CURR? CH1"))

    @property
    def ch1_voltage_setpoint(self) -> float:
        return float(self._query("CH1:VOLT?"))

    @ch1_voltage_setpoint.setter
    def ch1_voltage_setpoint(self, voltage: float):
        self.voltage_setpoint(voltage, 1)

    @property
    def ch1_current_setpoint(self) -> float:
        return float(self._query("CH1:CURR?"))

    @ch1_current_setpoint.setter
    def ch1_current_setpoint(self, current: float):
        self.current_setpoint(current, 1)

    @property
    def ch2_power(self) -> float:
        return self.power(2)

    @property
    def ch2_voltage(self) -> float:
        return float(self._query("MEAS:VOLT? CH2"))

    @property
    def ch2_current(self) -> float:
        return float(self._query("MEAS:CURR? CH2"))

    @property
    def ch2_voltage_setpoint(self) -> float:
        return float(self._query("CH2:VOLT?"))

    @ch2_voltage_setpoint.setter
    def ch2_voltage_setpoint(self, voltage: float):
        self.voltage_setpoint(voltage, 2)

    @property
    def ch2_current_setpoint(self) -> float:
        return float(self._query("CH2:CURR?"))

    @ch2_current_setpoint.setter
    def ch2_current_setpoint(self, current: float):
        self.current_setpoint(current, 2)
