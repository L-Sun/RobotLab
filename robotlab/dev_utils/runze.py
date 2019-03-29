import logging
import functools
import serial
from enum import Enum, unique
from traceback import extract_stack
logging.basicConfig(level=logging.DEBUG)


@unique
class RunzeCommand(Enum):
    get_maxspeed = 0x27
    get_resetspeed = 0x2B
    set_speed = 0x4B
    get_position = 0x66
    get_aisle = 0x3E
    polling = 0x4A
    pump_valve_polling = 0x4D
    push = 0x42
    pull = 0x43
    switch = 0x44
    reset = 0x45
    stop = 0x00


@unique
class RunzeStatus(Enum):
    normal = 0x00
    frame_error = 0x01
    param_error = 0x02
    opticalcoupler_error = 0x03
    busy = 0x04
    locked = 0x05
    need_polling = 0xFE
    unknown_error = 0xFF

    not_linked = 0xE0
    do_nothing = 0xEE


def pack(address, cmd, param):
    head = 0xCC
    foot = 0xDD
    result = bytearray([head, address, cmd.value])
    result += param.to_bytes(2, "little")
    result.append(foot)
    # sum verify
    result += sum(result).to_bytes(2, "little")
    return result


def unpack(data):
    """
    Return: Status, Value
    """

    data = bytearray(data)
    try:
        assert verify(data)
    except:
        logging.error("Verify failed. Bytes: %s" % data)
        raise type('VerifyError', (Exception,), dict())

    return RunzeStatus(int(data[2])), int.from_bytes(data[3:5], "little")


def verify(data):
    if len(data) != 8:
        logging.error("Data is not 8 bytes.")
        return False

    if sum(data[:-2]) != int.from_bytes(data[-2:], "little"):
        logging.error("Sclearum verify failed.")
        return False

    return True


class RunzeMixIn(object):
    def __init__(self, name, port, address):
        super(RunzeMixIn, self).__init__()
        self.name = name
        self.address = address
        self.timeout = 0.1
        self.port = serial.Serial(port=port, timeout=self.timeout)
        if port is None:
            logging.error("Serial port open failed.")

    def __send(self, cmd, param=0):
        status, value = None, 0
        self.port.flush()
        self.port.write(pack(self.address, cmd, param))
        data = self.port.read(16)
        data = data[:8] if len(data) == 8 else data[8:]
        try:
            status, value = unpack(data)
        except:
            status, value = RunzeStatus.do_nothing, 0

        return status, value

    def _send(self, cmd, param=0):
        if not extract_stack()[-2][2] == "_send":
            logging.debug("Send: %s param: %d." % (cmd.name, param))
        # check is the device normal.
        status, value = None, 0
        s1 = self.__send(RunzeCommand.polling)[0]
        if self.name == "pump":
            s2 = self.__send(RunzeCommand.pump_valve_polling)[0]
            if s1 != RunzeStatus.normal:
                status = s1
            elif s2 != RunzeStatus.normal:
                status = s2
            else:
                status = RunzeStatus.normal
        else:
            status = s1

        if status == RunzeStatus.normal:
            status, value = self.__send(cmd, param)
            # get true value
            if status == RunzeStatus.need_polling:
                if cmd == RunzeCommand.switch and self.name == "pump":
                    status, value = self.__send(
                        RunzeCommand.pump_valve_polling)
                else:
                    status, value = self.__send(RunzeCommand.polling)
        elif status == RunzeStatus.busy:
            return self._send(cmd, param)
        else:
            logging.error("Error: %s" % status.name)

        return value

    def isLinked(self):
        try:
            self._send(RunzeCommand.polling)
        except:
            return False
        return True
