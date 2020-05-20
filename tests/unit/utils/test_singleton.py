from cellengine.utils.singleton import Borg, Singleton


class ExampleBorg(Borg):
    pass


def test_should_save_state():
    borg = Borg()
    child = ExampleBorg()

    borg.var = "foo"
    assert child.var == "foo"


class ExampleSingleton(metaclass=Singleton):
    def __init__(self):
        self.val = 42


def test_should_get_same_object_on_singleton_init():
    t1 = ExampleSingleton()
    t2 = ExampleSingleton()

    assert t1.val == t2.val
    assert t1 is t2
