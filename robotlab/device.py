from robotlab.math_utils import Vector, Matrix, clip
from robotlab.dev_utils import SlideMixIn
from robotlab.dev_utils import RunzeCommand, RunzeMixIn
import logging
import time

logging.basicConfig(level=logging.DEBUG)


class Device(object):
    def __init__(self, name, **kw):
        super(Device, self).__init__(name=name, **kw)
        self.name = name


class Slide(Device, SlideMixIn):
    def __init__(self):
        super(Slide, self).__init__("slide")
        self._curr_point = Vector(0, 0)
        self._boundary = Vector(300, 200)
        self.speed = 30   # mm per s

    def __del__(self):
        self.reset()

    def move_to_point(self, p):
        v = self._clip(p - self._curr_point)
        t = v.length / self.speed
        self._move(v, t)
        self._curr_point += v

    def move(self, v):
        v = self._clip(v)
        self._move(v, v.length / self.speed)
        self._curr_point += v

    def reset(self):
        self._up()
        self.move_to_point(Vector(0, 0))

    def up(self):
        self._up()

    def down(self):
        self._down()

    def _clip(self, v):
        p = self._curr_point
        b = self._boundary
        k1 = 1 if v[0] == 0 else clip(v[0], -p[0], b[0]-p[0]) / v[0]
        k2 = 1 if v[1] == 0 else clip(v[1], -p[1], b[1]-p[1]) / v[1]
        k = min(k1, k2)
        ret = k * v
        if 0 <= k < 1:
            logging.warning("Move vector was cliped. Clip reslut is %s" % ret)
        return ret


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
        self.set_speed(200)
        self._send(RunzeCommand.reset)
        self.__update_position()

    @property
    def speed(self):
        return self.__speed

    def set_speed(self, value):
        if value < 0 or value > 200:
            logging.warning("speed can out of 0 and 200.")
            return
        self._send(RunzeCommand.set_speed, value)
        self.__speed = self._send(RunzeCommand.get_maxspeed)

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
