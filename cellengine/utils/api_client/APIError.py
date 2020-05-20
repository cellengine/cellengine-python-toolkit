import attr


@attr.s(auto_exc=True)
class APIError(BaseException):
    url = attr.ib()
    status_code = attr.ib()
    message = attr.ib()

    def __str__(self):
        if self.status_code:
            return "CellEngine API: status code {} != 200 for URL {} -- {}".format(
                self.status_code, self.url, self.message
            )

        else:
            return "Cellengine API: can't reach service for URL {} -- {}".format(
                self.url, self.message
            )
