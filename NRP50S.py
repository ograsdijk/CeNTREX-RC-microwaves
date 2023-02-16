import pyvisa


class NRP50S:
    def __init__(self, resource_name: str):
        rm = pyvisa.ResourceManager()
        self.dev = rm.open_resource(resource_name)
        self.dev.read_termination = "\n"

    def _query(self, command: str) -> str:
        return self.dev.query(command)

    def _write(self, command: str):
        self.dev.write(command)

    @property
    def frequency(self) -> float:
        return float(self._query("SENS:FREQ?"))

    @frequency.setter
    def frequency(self, frequency: float):
        self._write(f"SENS:FREQ {frequency}")
        assert frequency == self.frequency

    @property
    def average(self) -> bool:
        response = self._query("SENS:TRAC:AVER:STAT?")
        return bool(int(response))

    @average.setter
    def average(self, state: bool):
        if state:
            _state = "ON"
        else:
            _state = "OFF"
        self._write(f"SENS:TRAC:AVER:STAT {_state}")
        assert state == self.average

    @property
    def average_count(self) -> int:
        return self._query("SENS:TRAC:AVER:COUN?")

    @average_count.setter
    def average_count(self, count: int):
        self._write(f"SENS:TRAC:AVER:COUN {count}")
        assert count == self.average_count

    def initiate(self):
        self._write("INIT")

    def fetch(self) -> float:
        return float(self._query("FETCH?"))
