# TODO
# - open the window 10 min to DEHUM when temp out is very cold (or hot)
# - add margin (window should open to cool the room from 20.06 to 20 ?)
# - handle when the user open (or close) the window mannualy
# - communication between APP and WINDOW

from phidgets.motor import Motor
from phidgets.hub import Hub
import time

# Window actions
NOT = "nothing"
HEAT = "heating"
COOL = "cooling"
DEHUM = "dehumidification"

# Represent the smat window
class Window:
    def __init__(self, temp_desired = 20, max_hum = 70):
        self.is_open = False
        self.mode_auto = True
        self.state = []

        self.temp_desired = temp_desired
        self.max_hum = max_hum

        self.motor = Motor()
        self.hub = Hub()

        self.temp_in = self.hub.get_temp_in()
        self.temp_out = self.hub.get_temp_out()

        self.humidity = self.hub.get_humidity()

    # Open the window (use motor)
    def open(self):
        print("open")
        self.is_open = True
        self.motor.set_position(30)

    # Close the window (use motor)
    def close(self):
        print("close")
        self.is_open = False
        self.motor.set_position(0)

    # Get measures from the 3 sensors (2x temp, 1x humidity)
    def get_measures(self):
        self.temp_in = self.hub.get_temp_in()
        self.temp_out = self.hub.get_temp_out()
        self.humidity = self.hub.get_humidity()

        print(self.temp_in)
        print(self.temp_out)
        print(self.humidity)

    # Return string of current action(s) of window (Example: "heating and DEHUMidification")
    def repr_state(self):
        if len(self.state) == 0 :
            return "Nothing"

        repr = self.state[0]
        for i in range(len(self.state)-1):
            repr = repr + " and " + self.state[i+1]

        return repr


    # Define the behavior of the window in function of the measures and its current state
    def behavior(self):
        self.state = []

        self.get_measures()
        
        # Reasons why whe should open the window
        too_cold_in = self.temp_in < self.temp_desired and self.temp_out > self.temp_in
        too_hot_in = self.temp_in > self.temp_desired and self.temp_out < self.temp_in
        too_hum_in = self.humidity > self.max_hum

        if too_cold_in:
            self.state.append(HEAT)

        if too_hot_in:
            self.state.append(COOL)

        if too_hum_in:
            self.state.append(DEHUM)

        # If window already open
        if self.is_open :
            # If no need to HEAT, COOL or DEHUM => close
            # Else => keep open
            if len(self.state) == 0:
                self.close()
                print(f"Window closed (Temp inside = {self.temp_in}°C | Temp outside = {self.temp_out}°C | Humidity = {self.humidity})")

        # If window closed
        else:
            # If need to HEAT, COOL or DEHUM => open
            # Else => keep closed
            if len(self.state) > 0 :
                self.open()
                print(f"Window opened for {self.repr_state()} (Temp inside = {self.temp_in}°C | Temp outside = {self.temp_out}°C | Humidity = {self.humidity})")


# Initiate window
w = Window()
while w.mode_auto:
    w.behavior()
    time.sleep(2)

