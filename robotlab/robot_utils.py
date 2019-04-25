import logging


def pack(address, cmd, param=0):
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
    if verify(data) is not True:
        return

    return int(data[2]), int.from_bytes(data[3:5], "little")


def verify(data):
    if type(data) not in (bytes, bytearray):
        logging.error("command is not type of bytes.")
        return False

    if len(data) != 8:
        logging.error("command is not 8 bytes.")
        return False

    if sum(data[:-2]) != int.from_bytes(data[-2:], "little"):
        logging.error("command sum verify failed.")
        return False

    return True
