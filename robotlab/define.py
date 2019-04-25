from enum import Enum, unique


@unique
class Command(Enum):
    get_maxspeed = 0x27
    get_resetspeed = 0x2B
    set_speed = 0x4B
    get_position = 0x66
    get_aisle = 0x3E
    get_pump_valve_direction = 0x68
    polling = 0x4A
    valve_polling = 0x4D
    push = 0x42
    pull = 0x43
    switch = 0x44
    reset = 0x45
    stop = 0x00


class Status(object):
    not_linked = 0xFF
    normal = 0x00
    error = {
        0x01: "Frame error",
        0x02: "Param error",
        0x03: "Opticalcoupler error",
        0xFF: "Unknown error",
    }
    busy = 0x04
    locked = 0x05
    need_polling = 0xFE
