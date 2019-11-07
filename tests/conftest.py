import pytest


"""
Run tests with ``python -m pytest``.

Fixtures are defined in cellengine-python-toolkit/tests/tests/fixtures.
You can write new fixtures in new files here, or in existing .py files.
Fixtures in the ..tests/fixtures folder can use other fixtures in that folder.

Fixtures must be imported below using the `pytest_plugins` list.
When writing new fixtures, the ``pytest-vcr`` plugin is not called, as
it is with other tests. Use the "fixture_vcr" instance of VCR to write fixtures.

When writing new tests, ``pytest-vcr`` hooks tests to VCR. Use the
@pytest.mark.vcr decorator to make a .yaml with the same name as the test.

For unknown reasons, ``pytest-vcr`` fails to filter the headers for a
DELETE requests. Thus, "test_base_delete" is an unsafe test, as it saves a
login token. I have opened an issue on ``pytest-vcr``, but for now, if you
remake "test_base_delete.yaml", delete the two lines with the login token.
"""

pytest_plugins = [
    "fixtures.api-base",
    "fixtures.api-experiments",
    "fixtures.api-fcsfiles",
    "fixtures.api-compensations",
    "fixtures.api-gates",
    "fixtures.api-scalesets",
    "fixtures.api-populations",
]
