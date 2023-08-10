import pytest
import time
import struct
import binascii
from datetime import datetime
from cellengine.utils.generate_id import generate_id, get_id_timestamp, OID


def test_generates_an_id():
    _id = generate_id()
    assert type(_id) is str
    assert len(_id) == 24


def test_generates_unique_ids():
    id_list = []
    for _ in range(0, 1000):
        _id = generate_id()
        assert _id not in id_list
        id_list.append(_id)


def test_counter_overflow(monkeypatch):
    # Spec-test to check counter overflows from max value to 0.
    monkeypatch.setattr(OID, "_inc", OID._max_counter_value, raising=False)
    generate_id()
    assert OID._inc == 0


@pytest.fixture
def patch_time(monkeypatch):
    def faketime():
        return 1578934545.1363432

    monkeypatch.setattr(time, "time", faketime)


def test_get_id_timestamp(patch_time):
    _id = generate_id()
    ts = get_id_timestamp(_id)
    assert ts == datetime.utcfromtimestamp(int(time.time()))


def test_timestamp_values():
    # Spec-test to check timestamp field is interpreted correctly.
    TEST_DATA = {
        0x00000000: (1970, 1, 1, 0, 0, 0),
        0x7FFFFFFF: (2038, 1, 19, 3, 14, 7),
        0x80000000: (2038, 1, 19, 3, 14, 8),
        0xFFFFFFFF: (2106, 2, 7, 6, 28, 15),
    }

    def generate_id_with_timestamp(timestamp):
        """Generate an id with a specific timestamp"""
        oid = generate_id()
        _, trailing_bytes = struct.unpack(">IQ", binascii.unhexlify(oid))
        new_oid = struct.pack(">IQ", timestamp, trailing_bytes)
        return binascii.hexlify(new_oid)

    for tstamp, exp_datetime_args in TEST_DATA.items():
        oid = generate_id_with_timestamp(tstamp)
        generation_time = get_id_timestamp(oid)
        assert generation_time == datetime(*exp_datetime_args)
