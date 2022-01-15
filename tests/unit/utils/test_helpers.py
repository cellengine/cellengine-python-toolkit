import pytest
from cellengine.utils.helpers import alter_keys, to_camel_case


def test_alter_keys_converts_dict_to_camel_case():
    d = {
        "_id": "foo",
        "experiment_id": "bar",
        "fcsFile": "baz",
    }
    r = alter_keys(d, to_camel_case)
    assert {"_id", "experimentId", "fcsFile"} <= r.keys()


def test_alter_keys_converts_nested_dict_to_camel_case():
    d = {
        "_id": "foo",
        "experiment_id": "bar",
        "fcsFile": {
            "_id": "foo",
            "experiment_id": "bar",
            "fcsFile": "baz",
        },
    }
    r = alter_keys(d, to_camel_case)
    assert {"_id", "experimentId", "fcsFile"} <= r.keys()
    assert {"_id", "experimentId", "fcsFile"} <= r["fcsFile"].keys()


def test_alter_keys_converts_list_of_dicts_to_camel_case():
    d = [
        {
            "_id": "foo",
            "experiment_id": "bar",
            "fcsFile": "baz",
        },
        {
            "_id": "foo",
            "experiment_id": "bar",
            "fcsFile": "baz",
        },
    ]
    r = alter_keys(d, to_camel_case)
    assert {"_id", "experimentId", "fcsFile"} <= r[0].keys()


params = [
    "hello",
    1001,
    1.0,
    1j,
    [1, 2],
    ("a", "b"),
    range(4),
    True,
    b"foo",
    None,
]


@pytest.mark.parametrize("payload", params)
def test_alter_keys_returns_passed_payload_if_not_dict_or_list(payload):
    r = alter_keys(payload, to_camel_case)
    assert r == payload


def test_alter_keys_doesnt_mutate_or_drop_values():
    d = {
        "str": "str",
        "int": 20890,
        "float": 1.99,
        "complex": 1j,
        "list": [],
        "tuple": (),
        "range": range(2),
        "dict": {"a": 1},
        "set": {"a", "b"},
        "bool": True,
        "bytes": b"foo",
        "bytearray": bytearray(4),
        "None": None,
    }
    r = alter_keys(d, to_camel_case)
    assert r == d


def test_alter_keys_works_with_lists_inside_dicts():
    d = {
        "fcs_files": [
            {
                "access_key": "SOMEACCESSKEY",
                "secret_key": "somesecretkey",
            }
        ],
        "file_name": "my file",
    }
    r = alter_keys(d, to_camel_case)
    assert r == {
        "fcsFiles": [
            {
                "accessKey": "SOMEACCESSKEY",
                "secretKey": "somesecretkey",
            }
        ],
        "fileName": "my file",
    }
