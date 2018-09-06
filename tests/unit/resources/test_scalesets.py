import responses

from cellengine.resources.scaleset import ScaleSet


EXP_ID = "5d38a6f79fae87499999a74b"
SCALESET_ID = "5d38a6f79fae87499999a74c"


@responses.activate
def test_should_get_scaleset(ENDPOINT_BASE, client, scalesets):
    responses.add(
        responses.GET,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/scalesets",
        json=[scalesets],
    )
    ScaleSet.get(EXP_ID)


@responses.activate
def test_should_update_scaleset(ENDPOINT_BASE, client, scalesets):
    responses.add(
        responses.PATCH,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/scalesets/{SCALESET_ID}",
        json=scalesets,
    )
    s = ScaleSet(scalesets)
    s.name = "new scaleset"
    s.update()
