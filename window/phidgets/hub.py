from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
import time

class Hub:
    def __init__(self):
        self.temp_in = VoltageRatioInput()
        self.temp_in.setChannel(0)
        self.temp_in.openWaitForAttachment(1000)
        self.temp_in.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1124) # Precision temperature sensor

        self.temp_out = VoltageRatioInput()
        self.temp_out.setChannel(1)
        self.temp_out.openWaitForAttachment(1000)
        self.temp_out.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1125_TEMPERATURE) # Temperature sensor

        self.hum = VoltageRatioInput()
        self.hum.setChannel(2)
        self.hum.openWaitForAttachment(1000)
        self.hum.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1125_HUMIDITY) # Humidity

    def get_temp_in(self):
        return self.temp_in.getSensorValue()

    def get_temp_out(self):
        return self.temp_out.getSensorValue()

    def get_humidity(self):
        return self.hum.getSensorValue()

    def close_hub(self):
        self.temp_in.close()
        self.temp_out.close()
        self.hum.close()

        self.motor.close()