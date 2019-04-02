from robotlab.robotlab import Sampler
from robotlab.math_utils import Vector
import time

import ptvsd
ptvsd.enable_attach(('0.0.0.0', 5678))
ptvsd.wait_for_attach()


if __name__ == "__main__":
    rect1 = [
        Vector(0, 0),
        Vector(170, 0),
        Vector(170, 120),
        Vector(0, 120),
        Vector(0, 0),
    ]
    rect1 = [i+20 for i in rect1]
    rect2 = [
        Vector(0, 0),
        Vector(150, 0),
        Vector(150, 100),
        Vector(0, 100),
        Vector(0, 0),
    ]
    rect2 = [i+20+Vector(10, 10) for i in rect2]

    s = Sampler()

    s.open_port('v1-9')
    s.pump.reset()

    s.open_port('v1-1')
    s.pump.pull(5)
    s.pump.set_speed(1)
    s.slide.up()
    s.slide.move_to_point(Vector(35, 35))

    points = []
    back = False
    for i in range(10, 140, 10):
        for j in range(10, 90, 10):
            if not back:
                points.append(Vector(i+35, j+35))
            else:
                points.append(Vector(i+35, (90-j)+35))
        back = not back

    s.open_port('v2-1')
    for p in points:
        s.slide.move_to_point(p)
        s.pump.push(0.015)
        s.slide.down()
        s.slide.up()
        time.sleep(0.5)

    s.slide.up()
    s.pump.set_speed(200)

    s.open_port('v1-9')
    s.pump.reset()
