import pytest


@pytest.fixture(scope="session")
def scalesets():
    scalesets = {
        "__v": 0,
        "_id": "5d38a6f79fae87499999a74c",
        "experimentId": "5d38a6f79fae87499999a74b",
        "name": "Scale Set 1",
        "scales": [
            {
                "channelName": "FSC-A",
                "scale": {"maximum": 262144, "minimum": 1, "type": "LinearScale"},
            },
            {
                "channelName": "FSC-H",
                "scale": {"maximum": 262144, "minimum": 1, "type": "LinearScale"},
            },
            {
                "channelName": "FSC-W",
                "scale": {"maximum": 262144, "minimum": 1, "type": "LinearScale"},
            },
            {
                "channelName": "SSC-A",
                "scale": {"maximum": 262144, "minimum": 1, "type": "LinearScale"},
            },
            {
                "channelName": "SSC-H",
                "scale": {"maximum": 262144, "minimum": 1, "type": "LinearScale"},
            },
            {
                "channelName": "SSC-W",
                "scale": {"maximum": 262144, "minimum": 1, "type": "LinearScale"},
            },
            {
                "channelName": "Blue530-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "Blue695-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "Vio450-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "Vio525-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "Vio585-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "Vio605-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "Vio710-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "Vio655-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "Red780-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "UV530-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "Red670-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "YG780-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "YG610-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "YG670-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "Red730-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "YG710-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "UV450-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "YG582-A",
                "scale": {
                    "cofactor": 150,
                    "maximum": 262144,
                    "minimum": -200,
                    "type": "ArcSinhScale",
                },
            },
            {
                "channelName": "Time",
                "scale": {"maximum": 262144, "minimum": 1, "type": "LinearScale"},
            },
        ],
        "updated": "2019-07-24T18:44:07.664Z",
    }
    return scalesets
