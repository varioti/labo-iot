from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.TemperatureSensor import *
from Phidget22.Devices.HumiditySensor import *

import time

class Hub:
    def __init__(self):
        self.temp_out = VoltageRatioInput()
        self.temp_out.setIsHubPortDevice(True)
        self.temp_out.setHubPort(5)
        self.temp_out.openWaitForAttachment(5000)
        self.temp_out.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1124) # Temperature sensor

        self.temp_in = TemperatureSensor()
        self.temp_in.openWaitForAttachment(5000)

        self.hum = HumiditySensor()
        self.hum.openWaitForAttachment(5000)

        time.sleep(1)

    def get_temp_out(self):
        return self.temp_out.getSensorValue()

    def get_temp_in(self):
        return self.temp_in.getTemperature()

    def get_humidity(self):
        return self.hum.getHumidity()

    def close_hub(self):
        self.temp_in.close()
        self.temp_out.close()
        self.hum.close()
