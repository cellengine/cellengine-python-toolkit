class APIError(Exception):
    """Raised when the CellEngine API responds with an error."""

    url: str
    status_code: int
    message: str

    def __init__(self, url: str, status_code: int, message: str):
        self.url = url
        self.status_code = status_code
        self.message = message

    def __str__(self):
        if self.status_code:
            return (
                "CellEngine API responded with error status code {} for URL {} -- {}"
            ).format(self.status_code, self.url, self.message)

        else:
            return "Can't reach CellEngine API for URL {} -- {}".format(
                self.url, self.message
            )
