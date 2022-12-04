# TODO
# - open the window 10 min to DEHUM when temp out is very cold (or hot)
# - add margin (window should open to cool the room from 20.06 to 20 ?)

from sensors.window.phidgets.motor import Motor
from sensors.window.phidgets.hub import Hub

import random
from datetime import datetime

# Window actions
NOT = "Rien"
HEAT = "Chauffer"
COOL = "Refroidir"
DEHUM = "Déshumidifier"

# Represent the smat window
class Window:
    def __init__(self, temp_desired = 20, max_hum = 70, is_testing = False):
        self.is_testing = is_testing
        self.is_open = False
        self.mode_auto = True

        self.state = []
        self.last_dehum = None
        self.cooldown = False

        self.temp_desired = temp_desired
        self.max_hum = max_hum

        if not self.is_testing :
            self.motor = Motor()
            self.hub = Hub()

            self.temp_in = self.hub.get_temp_in()
            self.temp_out = self.hub.get_temp_out()

            self.humidity = self.hub.get_humidity()
        else :
            self.temp_in = random.uniform(15, 25)
            self.temp_out = random.uniform(15, 25)

            self.humidity = random.uniform(50, 100)

    # Set a new temp desired
    def set_temp_desired(self, new_value):
        self.temp_desired = new_value

    # Set a new temp desired
    def set_max_hum(self, new_value):
        self.max_hum = new_value

    # Open the window (use motor)
    def open(self):
        print("open")
        self.is_open = True
        if not self.is_testing :
            self.motor.set_position(70)

    # Close the window (use motor)
    def close(self):
        print("close")
        self.is_open = False
        if not self.is_testing :
            self.motor.set_position(0)

    # Set the window in auto mode (window will open and close by it-self)
    def set_auto(self):
        print("auto")
        self.mode_auto = True

    # Set the window in manual mode (window will only open if user do it)
    def set_manual(self):
        print("manual")
        self.mode_auto = False

    # Return open state of the window
    def get_is_open(self):
        return self.is_open

    # Get measures from the 3 sensors (2x temp, 1x humidity)
    def make_measures(self):
        if not self.is_testing :
            self.temp_in = round(self.hub.get_temp_in(), 1)
            self.temp_out = round(self.hub.get_temp_out(), 1)
            self.humidity = round(self.hub.get_humidity(), 2)

        else:
            self.temp_in = round(random.uniform(15, 25), 1)
            self.temp_out = round(random.uniform(15, 25), 1)
            self.humidity = round(random.uniform(50, 100), 2)

        print(self.temp_in)
        print(self.temp_out)
        print(self.humidity)

    # Returns current measures
    def get_measures(self):
        return self.temp_in, self.temp_out, self.humidity

    # Return string of current action(s) of window (Example: "heating and DEHUMidification")
    def repr_state(self):
        if len(self.state) == 0 :
            return "Aucune"

        repr = self.state[0]
        for i in range(len(self.state)-1):
            repr = repr + " et " + self.state[i+1]

        return repr
    
    # Set last dehum to now (init cooldown)
    def set_last_dehum(self):
        self.last_dehum = datetime.today()

    # Reset cooldown to False if there is 12 hours from last dehum
    def check_cooldown_dehum(self):
        if not self.last_dehum is None:
            if (datetime.today() - self.last_dehum).total_seconds()/3600 >= 12:
                self.cooldown = False

    # Check if time before closing window when DEHUM is finished and start cooldown
    def check_end_dehum(self, delta = 10):
        if not self.last_dehum is None:
            if (datetime.today() - self.last_dehum).total_seconds()/60 >= delta:
                self.set_last_dehum()
                self.cooldown = True

    # Define the behavior of the window in function of the measures and its current state
    def behavior(self):
        # Init
        self.state = []
        self.make_measures()
        
        # Reasons why whe should open the window (add margin)
        too_cold_in = self.temp_in + 0.2 < self.temp_desired and self.temp_out > self.temp_in + 0.5
        too_hot_in = self.temp_in - 0.2 > self.temp_desired and self.temp_out < self.temp_in - 0.5

        self.check_end_dehum(1) # Check if 10 minutes passed since window open for DEHUM (if yes cooldown started)
        # And window in cooldown
        too_hum_in = self.humidity > self.max_hum and (not self.cooldown or abs(self.temp_out - self.temp_in) < 2)

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
            if len(self.state) == 0 and self.mode_auto:
                self.close()
                return f"Fenêtre fermée (Temp int = {self.temp_in}°C | Temp ext = {self.temp_out}°C | Humidité = {self.humidity}%)"

        # If window closed
        else:
            # If need to HEAT, COOL or DEHUM => open
            # Else => keep closed
            if len(self.state) > 0 and self.mode_auto:
                self.open()

                # If window is only dehumidifiating the room we save the time in order to limit the time in which the window will stay open
                if self.state == [DEHUM]:
                    self.set_last_dehum()

                return f"Fenêtre ouverte pour {self.repr_state()} (Temp int = {self.temp_in}°C | Temp ext = {self.temp_out}°C | Humidité = {self.humidity})"

        return None

