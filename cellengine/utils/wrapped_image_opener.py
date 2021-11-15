from io import BytesIO

from cellengine.utils.singleton import AbstractSingleton


class WrappedImageOpener(metaclass=AbstractSingleton):
    """Display images with an already-installed image library, if possible"""

    def __init__(self):
        self.imager = self.get_imager()

    def open(self, data):
        if "PIL" in str(self.imager):
            image = self.imager.open(BytesIO(data))  # type: ignore
        elif "IPython" in str(self.imager):
            image = self.imager.display(self.imager.Image(data))  # type: ignore
        else:
            raise RuntimeError("Pillow or IPython is not installed.")
        return image

    def get_imager(self):
        try:
            from PIL import Image

            return Image
        except ModuleNotFoundError:
            try:
                from IPython import display

                return display
            except ModuleNotFoundError:
                raise ImportError(
                    "Try installing Pillow with `pip install pillow` \
                    or run in a Jupyter Notebook."
                )
