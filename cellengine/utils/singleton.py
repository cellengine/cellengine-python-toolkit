class Borg:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
