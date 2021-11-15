import attr


@attr.s(auto_exc=True)
class APIError(BaseException):
    url: str = attr.ib()
    status_code: int = attr.ib()
    message: str = attr.ib()

    def __str__(self):
        if self.status_code:
            return (
                "CellEngine API responded with error status code {} for URL {} -- {}"
            ).format(self.status_code, self.url, self.message)

        else:
            return "Can't reach CellEngine API for URL {} -- {}".format(
                self.url, self.message
            )
