import logging
import serial
import time

from robotlab.dev_utils import RunzeCommand, RunzeMixIn


class Device(object):
    def __init__(self, name, **kw):
        super(Device, self).__init__(name=name, **kw)
        self.name = name


class Slide(Device):
    def __init__(self):
        super(Slide, self).__init__("slide")
        # self.__curr_point =

    def move_to_point(self, x, y):
        pass

    def move(self, dx, dy):
        pass


class Pump(Device, RunzeMixIn):

    def __init__(self, port, address):
        super(Pump, self).__init__(name="pump", port=port, address=address)
        self.__address = address
        self.__step_per_volum = 480
        self.__boundary = 25  # mL

        # state
        self.__speed = self._send(RunzeCommand.get_maxspeed)
        self.__direction = None
        self.toggle(2)
        self.__position = self._send(
            RunzeCommand.get_position) / self.__step_per_volum

    def __update_position(self):
        value = self._send(RunzeCommand.get_position)
        self.__position = value / self.__step_per_volum

    def reset(self):
        self._send(RunzeCommand.reset)
        self.__update_position()

    @property
    def set_speed(self):
        return self.__speed

    def set_speed(self, value):
        self._send(RunzeCommand.set_speed, value)
        self.__speed = self._send(RunzeCommand.get_maxspeed)[1]

    @property
    def position(self):
        return self.__position

    @property
    def direction(self):
        return self.__direction

    def pull(self, volumn):
        if volumn == 0:
            return
        if self.__position + volumn > self.__boundary:
            logging.warning("volumn of pulling is out of boundary.")

        self._send(RunzeCommand.pull, volumn * self.__step_per_volum)
        self.__update_position()

    def push(self, volumn):
        if volumn == 0:
            return
        if self.__position - volumn < 0:
            logging.warning("volumn of pushing is out of boundary.")

        self._send(RunzeCommand.push, volumn * self.__step_per_volum)
        self.__update_position()

    def toggle(self, direction):
        if direction == self.__direction:
            return
        self._send(RunzeCommand.switch, direction)
        self.__direction = direction


class Valve(Device, RunzeMixIn):
    def __init__(self, port, address):
        super(Valve, self).__init__(name="valve", port=port, address=address)
        self.__boundary = 10  # port

        self.__aisle = self._send(RunzeCommand.get_aisle)

    def switch(self, aisle):
        if aisle == self.__aisle:
            return
        if not (0 < aisle <= self.__boundary):
            logging.error("aisle out of boundary")
            return

        self._send(RunzeCommand.switch, aisle)
        self.__aisle = self._send(RunzeCommand.get_aisle)
