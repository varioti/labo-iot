from Phidget22.Phidget import *
from Phidget22.Devices.VoltageInput import *
import time

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

    def make_measure(self):
        if not self.simulate:
            self.nb_amp = self.sensor.getSensorValue()
        else:
            self.nb_amp = 3

        print(self.nb_amp)

    def get_amp(self):
        return self.nb_amp

    def get_watt(self):
        return self.nb_amp * self.nb_volt

    def get_annual_kwatt(self):
        return self.nb_amp * self.nb_volt * 24 * 365 / 1000

e1 = Energy(0,12,False)
e2 = Energy(2,12,False)
e3 = Energy(3,12,False)
while True:
    e1.make_measure()
    e2.make_measure()
    e3.make_measure()
    time.sleep(2)