import importlib.util
from io import BytesIO

from cellengine.utils.singleton import AbstractSingleton


class WrappedImageOpener(metaclass=AbstractSingleton):
    """Display images with an already-installed image library, if possible"""

    def __init__(self):
        imager = self.find_one_of_packages(["PIL.Image", "IPython.display"])
        if imager:
            self.imager = imager
        else:
            raise ImportError(
                "Try installing Pillow with `pip install pillow` \
                or run in a Jupyter Notebook."
            )

    def open(self, data):
        if "PIL" in str(self.imager):
            image = self.imager.open(BytesIO(data))
        elif "IPython" in str(self.imager):
            image = self.imager.display(self.imager.Image(data))
        return image

    def find_one_of_packages(self, package_names):
        """Find an image library or return None"""
        for package in package_names:
            try:
                lib = importlib.util.find_spec(package)
                return lib.loader.load_module()
            except Exception:
                continue
