from phidgets.motor import Motor
from phidgets.hub import Hub
import time

class Window:
    def __init__(self):
        self.is_open = False
        self.mode_auto = True

        self.motor = Motor()
        self.hub = Hub()

        self.temp_in = self.hub.get_temp_in()
        self.temp_out = self.hub.get_temp_out()

        self.hum = self.hub.get_humidity()

    def open(self):
        print("open")
        self.is_open = True
        self.motor.set_position(30)

    def close(self):
        print("close")
        self.is_open = False
        self.motor.set_position(0)

    def get_measures(self):
        self.temp_in = self.hub.get_temp_in()
        self.temp_out = self.hub.get_temp_out()
        self.hum = self.hub.get_humidity()

        print(self.temp_in)
        print(self.temp_out)
        print(self.hum )

w = Window()
while True:
    w.get_measures()
    print("-----")
    time.sleep(2)

