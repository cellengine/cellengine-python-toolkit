import pytest


@pytest.fixture(scope="session")
def attachments():
    attachments = [
        {
            "_id": "5e3a5abf62c76b4f1b207b5b",
            "size": 20890,
            "md5": "545e35f5cb5317529c6e9e3cf88bff6f",
            "filename": "config.h",
            "experimentId": "5e26b3f94b14014f02b1ecda",
        }
    ]
    return attachments
