class Command(object):
    query_maxspeed = 0x27
    query_resetspeed = 0x2B
    polling = 0x4A
    push = 0x42
    pull = 0x43
    switch = 0x44
    pump_reset = 0x45
    stop = 0x00
    set_speed = 0x4B
    valve_reset = 0x4C
    read_position = 0x66
    clear_position = 0x67  # need to be called after reset pump


class Status(object):
    Normal = 0x00
    Error = {
        0x01: "Frame error",
        0x02: "Param error",
        0x03: "Opticalcoupler error",
        0xFF: "Unknown error",
    }
    Warning: {
        0x04: "Rotor busy",
        0x05: "Rotor locked",
    }
    Need_polling = 0xFE
