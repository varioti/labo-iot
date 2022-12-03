from Phidget22.Phidget import *
from Phidget22.Devices.VoltageInput import *
import time
import random

class Energy:
    def __init__(self, hub_port=0, nb_volt=12, simulate=False):
        self.nb_volt = nb_volt
        self.nb_amp = 0
        
        self.simulate = simulate
        if not self.simulate:
            self.sensor = VoltageInput()
            self.sensor.setIsHubPortDevice(True)
            self.sensor.setHubPort(hub_port)
            self.sensor.openWaitForAttachment(5000)
            self.sensor.setSensorType(VoltageSensorType.SENSOR_TYPE_3500)

    # Get measure from phidget
    def make_measure(self):
        if not self.simulate:
            self.nb_amp = self.sensor.getSensorValue()
        else:
            self.nb_amp = random.uniform(0.5, 4.5)

    # Get AC value (in AMP)
    def get_amp(self):
        return self.nb_amp

    # Get Power value (in WATT)
    def get_watt(self):
        return self.nb_amp * self.nb_volt

    # Get Annual Energy value (in kWATT/HOUR)
    def get_annual_kwatt(self):
        return self.nb_amp * self.nb_volt * 24 * 365 / 1000