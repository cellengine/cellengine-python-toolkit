import pytest


@pytest.fixture(scope="session")
def rectangle_gate():
    return specific_gate("RectangleGate")


@pytest.fixture(scope="session")
def ellipse_gate():
    return specific_gate("EllipseGate")


@pytest.fixture(scope="session")
def polygon_gate():
    return specific_gate("PolygonGate")


@pytest.fixture(scope="session")
def range_gate():
    return specific_gate("RangeGate")


@pytest.fixture(scope="session")
def quadrant_gate():
    return specific_gate("QuadrantGate")


@pytest.fixture(scope="session")
def split_gate():
    return specific_gate("SplitGate")


def specific_gate(gate_type):
    gates = {
        "EllipseGate": {
            "__v": 0,
            "_id": "5d9401613afd657e233843b3",
            "experimentId": "5d38a6f79fae87499999a74b",
            "fcsFileId": None,
            "gid": "5d9401613afd657e233843b4",
            "model": {
                "ellipse": {
                    "angle": -0.16875182756633697,
                    "center": [259441.51377370575, 63059.462213950595],
                    "major": 113446.7481834943,
                    "minor": 70116.01916918601,
                },
                "label": [263044.8350515464, 66662.79381443298],
                "locked": False,
            },
            "name": "ellipse-gui",
            "names": [],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "EllipseGate",
            "xChannel": "FSC-A",
            "yChannel": "FSC-H",
        },
        "PolygonGate": {
            "__v": 0,
            "_id": "5d9365b5117dfb76dd9ed4af",
            "experimentId": "5d38a6f79fae87499999a74b",
            "fcsFileId": None,
            "gid": "5d9365b5117dfb76dd9ed4b0",
            "model": {
                "label": [59456.113402061856, 193680.53608247422],
                "locked": False,
                "polygon": {
                    "vertices": [
                        [59456.113402061856, 184672.1855670103],
                        [141432.10309278348, 181068.84536082475],
                        [82877.82474226804, 124316.23711340204],
                        [109002.0412371134, 63960.28865979381],
                        [44141.9175257732, 76571.97938144332],
                        [27926.886597938144, 107200.37113402062],
                        [10811.0206185567, 143233.77319587627],
                        [58555.278350515466, 145936.27835051547],
                    ]
                },
            },
            "name": "poly_gate",
            "names": [],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "PolygonGate",
            "xChannel": "FSC-A",
            "yChannel": "FSC-H",
        },
        "QuadrantGate": {
            "__v": 0,
            "_id": "5db01cb2c2db443d7b99ad2a",
            "experimentId": "5d38a6f79fae87499999a74b",
            "fcsFileId": None,
            "gid": "5db01cb2dd879d32d2ccde05",
            "model": {
                "gids": [
                    "5db01cb2e4eb52e0c1047306",
                    "5db01cb265909ddcfd6e2807",
                    "5db01cb2486959d467563e08",
                    "5db01cb21b8e42bc6499c609",
                ],
                "labels": [[1, 1], [-200, 1], [-200, -200], [1, -200]],
                "locked": False,
                "quadrant": {
                    "angles": [
                        1.5707963267948966,
                        3.141592653589793,
                        4.71238898038469,
                        0,
                    ],
                    "x": 160000,
                    "y": 200000,
                },
                "skewable": False,
            },
            "names": ["my gate (UR)", "my gate (UL)", "my gate (LL)", "my gate (LR)"],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "QuadrantGate",
            "xChannel": "FSC-A",
            "yChannel": "FSC-W",
        },
        "RangeGate": {
            "__v": 0,
            "_id": "5d960ae0086ef688093cfb9c",
            "experimentId": "5d38a6f79fae87499999a74b",
            "fcsFileId": None,
            "gid": "5d960ae01070fcef1c1f5a04",
            "model": {
                "label": [53.802, 0.5],
                "locked": False,
                "range": {"x1": 12.502, "x2": 95.102, "y": 0.5},
            },
            "name": "my gate",
            "names": [],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "RangeGate",
            "xChannel": "FSC-A",
            "yChannel": "FSC-W",
        },
        "RectangleGate": {
            "__v": 0,
            "_id": "5d8d34994e84a1e661f157a1",
            "experimentId": "5d38a6f79fae87499999a74b",
            "fcsFileId": None,
            "gid": "5d8d34993b0bb307a31d9d04",
            "model": {
                "label": [130000, 145000],
                "locked": False,
                "rectangle": {"x1": 60000, "x2": 200000, "y1": 75000, "y2": 215000},
            },
            "name": "test_rect_gate",
            "names": [],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "RectangleGate",
            "xChannel": "FSC-W",
            "yChannel": "FSC-A",
        },
        "SplitGate": {
            "__v": 0,
            "_id": "5db02affb5cde93d7c922f93",
            "experimentId": "5d38a6f79fae87499999a74b",
            "fcsFileId": None,
            "gid": "5db02aff2299543efa9f7e00",
            "model": {
                "gids": ["5db02aff9375ffe04e55b801", "5db02aff556563a0f01c7a02"],
                "labels": [[-199.9, 0.916], [0.9, 0.916]],
                "locked": False,
                "split": {"x": 160000, "y": 1},
            },
            "names": ["my gate (L)", "my gate (R)"],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "SplitGate",
            "xChannel": "FSC-A",
        },
    }
    return gates[gate_type]


@pytest.fixture(scope="session")
def gates():
    gates = [
        {
            "__v": 0,
            "_id": "5d64abe2ca9df61349ed8e90",
            "experimentId": "5d64abe2ca9df61349ed8e78",
            "fcsFileId": None,
            "gid": "5d38b0ba417e4bc767a428a1",
            "model": {
                "gids": [
                    "5d38b0ba417e4bc767a4289d",
                    "5d38b0ba417e4bc767a4289e",
                    "5d38b0ba417e4bc767a4289f",
                    "5d38b0ba417e4bc767a428a0",
                ],
                "labels": [[262144, 262144], [1, 262144], [1, 1], [262144, 1]],
                "locked": False,
                "quadrant": {
                    "angles": [1.5707963267949, 3.14159265358979, 4.71238898038469, 0],
                    "x": 70000,
                    "y": 60000,
                },
                "skewable": False,
            },
            "names": [
                "test gate 2 (UR)",
                "test gate 2 (UL)",
                "test gate 2 (LL)",
                "test gate 2 (LR)",
            ],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "QuadrantGate",
            "xChannel": "FSC-A",
            "yChannel": "FSC-W",
        },
        {
            "__v": 0,
            "_id": "5d64abe2ca9df61349ed8e91",
            "experimentId": "5d64abe2ca9df61349ed8e78",
            "fcsFileId": None,
            "gid": "5d38dea2417e4bc767a428a1",
            "model": {
                "gids": [
                    "5d38dea2417e4bc767a4289d",
                    "5d38dea2417e4bc767a4289e",
                    "5d38dea2417e4bc767a4289f",
                    "5d38dea2417e4bc767a428a0",
                ],
                "labels": [[262144, 262144], [1, 262144], [1, 1], [262144, 1]],
                "locked": False,
                "quadrant": {
                    "angles": [1.5707963267949, 3.14159265358979, 4.71238898038469, 0],
                    "x": 80000,
                    "y": 90000,
                },
                "skewable": False,
            },
            "names": ["subtest (UR)", "subtest (UL)", "subtest (LL)", "subtest (LR)"],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "QuadrantGate",
            "xChannel": "FSC-A",
            "yChannel": "FSC-W",
        },
        {
            "__v": 0,
            "_id": "5d64abe2ca9df61349ed8e92",
            "experimentId": "5d64abe2ca9df61349ed8e78",
            "fcsFileId": None,
            "gid": "5d52cc1bf233dcda26a5f857",
            "model": {
                "label": [10811.0206185567, 42340.24742268041],
                "locked": False,
                "rectangle": {
                    "x1": 7207.680412371134,
                    "x2": 46844.422680412375,
                    "y1": 5406.01030927835,
                    "y2": 31530.22680412371,
                },
            },
            "name": "rect",
            "names": [],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "RectangleGate",
            "xChannel": "FSC-A",
            "yChannel": "FSC-H",
        },
        {
            "__v": 0,
            "_id": "5d64abe2ca9df61349ed8e93",
            "experimentId": "5d64abe2ca9df61349ed8e78",
            "fcsFileId": None,
            "gid": "5d52cc69f233dcda26a5f859",
            "model": {
                "gids": [
                    "5d52cc69f233dcda26a5f85a",
                    "5d52cc69f233dcda26a5f85b",
                    "5d52cc69f233dcda26a5f85c",
                    "5d52cc69f233dcda26a5f85d",
                ],
                "labels": [
                    [233317.2783505154, 248631.4742268041],
                    [36034.402061855675, 248631.4742268041],
                    [36034.402061855675, 14414.360824742267],
                    [233317.2783505154, 14414.360824742267],
                ],
                "locked": False,
                "quadrant": {
                    "angles": [
                        0,
                        4.71238898038469,
                        3.141592653589793,
                        1.5707963267948966,
                    ],
                    "x": 22521.876288659794,
                    "y": 23422.711340206188,
                },
            },
            "names": ["quad (UR)", "quad (UL)", "quad (LL)", "quad (LR)"],
            "parentPopulationId": "5d64abe2ca9df61349ed8e89",
            "tailoredPerFile": False,
            "type": "QuadrantGate",
            "xChannel": "FSC-A",
            "yChannel": "FSC-H",
        },
        {
            "_id": "5da630b08617fbdf268a4cb0",
            "experimentId": "5d64abe2ca9df61349ed8e78",
            "fcsFileId": None,
            "gid": "5da630b06738e73f7b43c000",
            "model": {
                "label": [53.802, 16520.6],
                "locked": False,
                "rectangle": {"x1": 12.502, "x2": 95.102, "y1": 1020, "y2": 32021.2},
            },
            "name": "my gate",
            "names": [],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "RectangleGate",
            "xChannel": "FSC-A",
            "yChannel": "FSC-W",
        },
        {
            "_id": "5da631c7181375df27e9860a",
            "experimentId": "5d64abe2ca9df61349ed8e78",
            "fcsFileId": None,
            "gid": "5da631c76558ea6c860c2600",
            "model": {
                "label": [53.802, 16520.6],
                "locked": False,
                "rectangle": {"x1": 12.502, "x2": 95.102, "y1": 1020, "y2": 32021.2},
            },
            "name": "my gate",
            "names": [],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "RectangleGate",
            "xChannel": "FSC-A",
            "yChannel": "FSC-W",
        },
        {
            "_id": "5da632658617fbdf268a4cb2",
            "experimentId": "5d64abe2ca9df61349ed8e78",
            "fcsFileId": None,
            "gid": "5da632653ee1cd665ad69d01",
            "model": {
                "label": [53.802, 16520.6],
                "locked": False,
                "rectangle": {"x1": 12.502, "x2": 95.102, "y1": 1020, "y2": 32021.2},
            },
            "name": "my gate",
            "names": [],
            "parentPopulationId": None,
            "tailoredPerFile": False,
            "type": "RectangleGate",
            "xChannel": "FSC-A",
            "yChannel": "FSC-W",
        },
    ]
    return gates
