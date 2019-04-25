from robotlab.robotlab import Sampler
from robotlab.math_utils import Vector
import time
import json
import logging
import logging.config
import os

log_config_path = os.path.join(os.path.dirname(__file__), "log_conf.json")
with open(log_config_path, 'r', encoding='utf-8') as f:
    logging.config.dictConfig(json.load(f))

# import ptvsd
# ptvsd.enable_attach(('0.0.0.0', 5678))
# ptvsd.wait_for_attach()


class Port(object):

    sample = "v1-1"
    hcl_6 = "v1-2"
    hcl_0_1 = "v1-3"
    hno3_5 = "v1-4"
    hno3_0_5 = "v1-5"
    water = "v1-10"
    air = "v1-9"
    waste = "v2-10"


elution_logger = logging.getLogger("main.elution")


def elution(elute_port, sample_port, H1, H2, elute_speed, elute_volum=5):

    s = Sampler()

    def wash_column(repeat=3):
        s.slide.move_to_point(Vector(0, 0))
        for i in range(repeat):
            elution_logger.info("水洗柱子第%d次..." % (i+1))
            s.elute(Port.water, [elute_port], volum=5, speed=20)
        s.elute(Port.air, [elute_port], volum=5, speed=20)

    def stuff():
        s.elute(sample_port, [Port.waste], volum=2, speed=50,
                air_port=Port.air, air_volum=2)
        s.elute(H1, [Port.waste], volum=2, speed=50,
                air_port=Port.air, air_volum=2)
        s.elute(H2, [Port.waste], volum=2, speed=50,
                air_port=Port.air, air_volum=2)

    s.slide.move_to_point(Vector(50, 80))

    # 清空管道
    s.open_port(Port.waste)
    s.pump.reset()

    # stuff()

    # 洗淋公用管线
    s.wash(Port.water, [Port.waste], volum=20)
    time.sleep(5)

    s.slide.move_to_point(Vector(50, 80))

    # 洗柱子 H1
    elution_logger.info("洗柱子 H1...")
    s.slide.move(Vector(0, 24))
    s.elute(H1, [elute_port], volum=elute_volum,
            speed=elute_speed, air_port=Port.air, air_volum=2)

    # 进料液
    elution_logger.info("进料液...")
    s.slide.move(Vector(24, 0))
    s.elute(sample_port, [elute_port], volum=elute_volum, speed=elute_speed,
            air_port=Port.air, air_volum=2)

    s.slide.move(Vector(-48, -24))

    # H1
    for i in range(5):
        elution_logger.info("H1, 淋洗第%d管..." % (i+1))
        s.slide.move(Vector(24, 0))
        s.elute(H1, [elute_port], volum=elute_volum,
                speed=elute_speed, air_port=Port.air, air_volum=2)

    # H2
    for i in range(5):
        elution_logger.info("H2, 淋洗第%d管..." % (i+6))
        s.slide.move(Vector(24, 0))
        s.elute(H2, [elute_port], volum=elute_volum,
                speed=elute_speed, air_port=Port.air, air_volum=2)

    wash_column()


if __name__ == "__main__":
    elution_logger.info("123")
#     elution("v2-3", Port.sample, Port.hcl_6, Port.hcl_0_1, 12, 5)
