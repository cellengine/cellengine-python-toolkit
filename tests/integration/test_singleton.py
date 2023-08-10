from cellengine.utils.singleton import Singleton


class ExampleSingleton(metaclass=Singleton):
    def __init__(self):
        self.val = 42


def test_should_get_same_object_on_singleton_init():
    t1 = ExampleSingleton()
    t2 = ExampleSingleton()

    assert t1.val == t2.val
    assert t1 is t2
