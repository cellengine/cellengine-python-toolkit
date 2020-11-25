import os
import time
import struct
import binascii
from datetime import datetime
from random import SystemRandom


class OID:
    pass


OID._pid = os.getpid()
OID._max_counter_value = 0xFFFFFF
OID._inc = SystemRandom().randint(0, OID._max_counter_value)
OID._random = os.urandom(5)


def _random():
    """Generate a 5-byte random number once per process."""
    pid = os.getpid()
    PID = OID._pid
    if pid != PID:
        OID._pid = pid
        OID._random = os.urandom(5)
    return OID._random


def generate_id():
    """Generates a hexadecimal ID based on a mongoDB ObjectId"""
    # 4 bytes timestamp
    oid = struct.pack(">I", int(time.time()))

    # 5 bytes random
    oid += _random()

    # 3 bytes counter
    oid += struct.pack(">I", OID._inc)[1:4]
    OID._inc = (OID._inc + 1) % (OID._max_counter_value + 1)

    return binascii.hexlify(oid).decode()


def get_id_timestamp(_id):
    """Parse the timestamp from an ObjectId

    Args:
        _id: the ObjectId to parse

    Returns:
        datetime
    """
    oid = binascii.unhexlify(_id)
    timestamp = struct.unpack(">I", oid[0:4])[0]
    return datetime.utcfromtimestamp(timestamp)
