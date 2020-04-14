from cellengine.utils.singleton import Borg


class ExampleBorg(Borg):
    pass


def test_should_save_state():
    borg = Borg()
    child = ExampleBorg()

    borg.var = "foo"
    assert child.var == "foo"
