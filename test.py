from robotlab import Sampler, device

s = Sampler()
v = device.Valve("/dev/ttyACAM0", 0x1)
