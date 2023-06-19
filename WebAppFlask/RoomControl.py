import random
import threading


class RoomControl:
    livingRoom = "off"
    toilet = "off"
    temperature = round(random.uniform(22.0, 24.0), 1)
    kitchen = "off"
    room1 = "off"
    room2 = "off"

    @staticmethod
    def cycle_temp_update():
        RoomControl.temperature += random.uniform(-1, 1)
        RoomControl.temperature = round(RoomControl.temperature, 1)
        threading.Timer(5, RoomControl.cycle_temp_update).start()

    def __init__(self, context):
        context = context
        RoomControl.cycle_temp_update()

    def update_room_1(self):
        ...

    def update_room_2(self):
        ...

    def update_kitchen(self):
        ...

    def update_toilet(self):
        ...

    def update_living_room(self):
        ...

    def update_temperature_min(self, new_min):
        self.temperature2.min_temperature = new_min
        ...