# import ptvsd
# ptvsd.enable_attach(('0.0.0.0',5678))
# ptvsd.wait_for_attach()

from .device import Pump

p1 = Pump("/dev/ttyAMA0", 0x01)
