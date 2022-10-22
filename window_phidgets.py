from multiprocessing.connection import wait
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
import time

#Declare any event handlers here. These will be called every time the associated event occurs.

def onVoltageRatioChange(self, voltageRatio):
    # Change sensor type to Precision Temperature
    self.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1124)
    print("Temp [" + str(self.getChannel()) + "]: " + str(self.getSensorValue())+ str(self.getSensorUnit().symbol))

def main():
	#Create your Phidget channels
    voltageRatioInput0 = VoltageRatioInput()

	#Set addressing parameters to specify which channel to open (if any)
    voltageRatioInput0.setChannel(0)

	#Assign any event handlers you need before calling open so that no events are missed.
    voltageRatioInput0.setOnVoltageRatioChangeHandler(onVoltageRatioChange)

	#Open your Phidgets and wait for attachment
    voltageRatioInput0.openWaitForAttachment(5000)
    
    # Set interval between 2 measures
    voltageRatioInput0.setDataInterval(1000)

    # Change sensor type to Precision Temperature
    voltageRatioInput0.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1124)

    #Do stuff with your Phidgets here or in your event handlers.
    
    # Loop
    active = True
    while active :
        time.sleep(1)
        print("Temp [" + str(voltageRatioInput0.getChannel()) + "]: " + str(voltageRatioInput0.getSensorValue()) + str(voltageRatioInput0.getSensorUnit().symbol))
        if voltageRatioInput0.getSensorValue() > 24:
            print("Too hot")
            active = False

	#Close your Phidgets once the program is done.
    voltageRatioInput0.close()

main()