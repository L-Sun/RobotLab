import logging
import serial
from enum import Enum, unique
from traceback import extract_stack

runze_logger = logging.getLogger("main.device.runze")


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
class Status(Enum):
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
    except Exception:
        runze_logger.error("Verify failed. Bytes: %s" % data)
        raise type('VerifyError', (Exception,), dict())

    return Status(int(data[2])), int.from_bytes(data[3:5], "little")


def verify(data):
    if len(data) != 8:
        runze_logger.error("Data is not 8 bytes.")
        return False

    if sum(data[:-2]) != int.from_bytes(data[-2:], "little"):
        runze_logger.error("Sclearum verify failed.")
        return False

    return True


class RunzeMixIn(object):
    def __init__(self, name, port, address):
        super(RunzeMixIn, self).__init__()
        self.name = name
        self.address = address
        self.timeout = 0.2
        self.port = serial.Serial(port=port, timeout=self.timeout)
        if port is None:
            runze_logger.error("Serial port open failed.")

    def __send(self, cmd, param=0):
        status, value = None, 0
        self.port.write(pack(self.address, cmd, param))
        data = self.port.read(16)
        data = data[:8] if len(data) == 8 else data[8:]
        try:
            status, value = unpack(data)
        except Exception:
            status, value = Status.do_nothing, 0

        return status, value

    def _send(self, cmd, param=0):
        param = int(param)
        if not extract_stack()[-2][2] == "_send":
            runze_logger.debug("Send: %s param: %d." % (cmd.name, param))
        # check is the device normal.
        status, value = None, 0
        s1 = self.__send(RunzeCommand.polling)[0]
        if self.name == "pump":
            s2 = self.__send(RunzeCommand.pump_valve_polling)[0]
            if s1 != Status.normal:
                status = s1
            elif s2 != Status.normal:
                status = s2
            else:
                status = Status.normal
        else:
            status = s1

        if status == Status.normal:
            status, value = self.__send(cmd, param)
            # get true value
            if status == Status.need_polling:
                if cmd == RunzeCommand.switch and self.name == "pump":
                    status, value = self.__send(
                        RunzeCommand.pump_valve_polling)
                else:
                    status, value = self.__send(RunzeCommand.polling)
        elif status == Status.busy:
            while status == Status.busy:
                if cmd == RunzeCommand.switch and self.name == "pump":
                    status, value = self.__send(
                        RunzeCommand.pump_valve_polling)
                else:
                    status, value = self.__send(RunzeCommand.polling)
            return self._send(cmd, param)
        else:
            runze_logger.error("Error: %s" % status.name)

        return value

    def isLinked(self):
        try:
            self._send(RunzeCommand.polling)
        except Exception:
            return False
        return True
