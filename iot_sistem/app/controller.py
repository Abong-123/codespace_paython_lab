class ClimateController:
    def __init__(self):
        self.fan = False
        self.heater = False
        self.mode_auto = True

    def evaluate(self, temp: float):
        if not self.mode_auto:
            return False
        
        old_fan = self.fan
        old_heater = self.heater

        if temp >= 34:
            self.fan = True
            self.heater = False
        elif temp <= 18:
            self.fan = False
            self.heater = True
        else:
            self.fan = False
            self.heater = False
        
        if old_fan != self.fan or old_heater != self.heater:
            return True
        return False

