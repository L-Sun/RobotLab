import logging
from plotink import ebb_motion, ebb_serial

from robotlab.math_utils import Vector


class SlideMixIn(object):
    def __init__(self, name):
        self.name = name
        self.port = ebb_serial.openPort()
        if self.port is None:
            logging.error("Can not open the port of slide.")

    def _move(self, v, t):
        if int(v.length) == 0:
            return
        x, y = v.astype(int) * 100  # mm to um
        t = int(t * 1000)  # s to ms
        ebb_motion.doABMove(self.port, x, y, t)

    def _up(self):
        ebb_motion.sendPenUp(self.port, 100)

    def _down(self):
        ebb_motion.sendPenDown(self.port, 100)
