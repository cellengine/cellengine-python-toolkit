import importlib.util
from io import BytesIO

from cellengine.utils.singleton import Borg


class WrappedImage(Borg):
    """Display images with an already-installed image library, if possible"""

    def __init__(self):
        imager = self.find_one_of_packages(["PIL.Image", "IPython.display"])
        if imager:
            self.imager = imager
        else:
            raise ImportError(
                "You must install extras for this functionality. Try `pip install cellengine-python-toolkit[interactive]` or `pip install -e .[interactive]`."
            )

    def open(self, data):
        if "PIL" in str(self.imager):
            return self.imager.open(BytesIO(data))
        elif "IPython" in str(self.imager):
            return self.imager.display(self.imager.Image(data))

    def find_one_of_packages(self, package_names):
        """Find an image library or return None"""
        libstr = next(
            (package for package in package_names if importlib.util.find_spec(package)),
            None,
        )
        lib = importlib.util.find_spec(libstr)
        return lib.loader.load_module()
