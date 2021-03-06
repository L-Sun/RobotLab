from robotlab.device import Pump, Valve, Slide
from robotlab.math_utils import Vector

import time
import functools


class Robot(object):
    def __init__(self, name):
        self.name = name


class Sampler(Robot):
    def __init__(self):
        super(Sampler, self).__init__("Sampler")
        self.pump = Pump("/dev/ttyAMA0", 0x01)
        self.v1 = Valve("/dev/ttyAMA0", 0x02)
        self.v2 = Valve("/dev/ttyAMA0", 0x03)
        self.slide = Slide()

        self.ports = {
            **{('v1-%d' % i): (self.v1, i) for i in range(1, 11)},
            **{('v2-%d' % i): (self.v2, i) for i in range(1, 11)}
        }
        self.pump2valve = {
            self.v1: 1,
            self.v2: 2
        }

        self.isLocked = False

    def elute(self, elute_port, target_ports, volum, speed, **kw):
        for p in target_ports:
            self.open_port(elute_port)
            self.pump.set_speed(100)
            self.pump.pull(volum)
            time.sleep(1)
            # pump pull air
            if "air_port" in kw and "air_volum" in kw:
                self.open_port(kw["air_port"])
                self.pump.pull(kw["air_volum"])
                volum += kw["air_volum"]

            self.pump.set_speed(speed)
            self.open_port(p)
            self.pump.push(volum)

    def open_port(self, port):
        valve, port = self.ports[port]
        self.pump.toggle(self.pump2valve[valve])
        valve.switch(port)

    def etablish_coord(self):
        self.slide.down()
        self.slide.move_to_point(Vector(300, 0))
        self.slide.move_to_point(self.slide._boundary)
        self.slide.move_to_point(Vector(0, 200))
        self.slide.move_to_point(Vector(0, 0))
        self.slide.up()
