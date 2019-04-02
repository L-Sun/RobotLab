from robotlab.device import Pump, Valve, Slide
from robotlab.math_utils import Vector


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
            self.v1: 2,
            self.v2: 1
        }

    def wash(self, valve, water, volum):
        """ Wash all port

        Parameter:
            valve: target valve
            water: water port
            volum: volum of washing for every port
        """
        for port in self.ports.keys():
            if port == water or port[0:2] != valve:
                continue
            self.open_port(water)
            self.pump.pull(volum)
            self.open_port(port)
            self.pump.push(volum)

    def elute(self, elute_port, target_ports, volum, speed):
        for p in target_ports:
            self.open_port(elute_port)
            self.pump.set_speed(200)
            self.pump.pull(volum)
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
