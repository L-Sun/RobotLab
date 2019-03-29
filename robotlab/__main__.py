from robotlab.device import Pump, Valve
# import ptvsd
# ptvsd.enable_attach(('0.0.0.0', 5678))
# ptvsd.wait_for_attach()

p1 = Pump("/dev/ttyAMA0", 0x01)
v1 = Valve("/dev/ttyAMA0", 0x02)
v2 = Valve("/dev/ttyAMA0", 0x03)

# p1.reset()
print(p1.direction)
p1.toggle(1)
p1.pull(20)
print(p1.direction)
# p1.toggle(2)
# p1.push(5)
print(p1.direction)

p1.reset()

for i in range(1, 11):
    v1.switch(i)
    v2.switch(i)
