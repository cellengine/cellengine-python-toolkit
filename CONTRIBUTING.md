## Contributing

### Running tests

Tests run with `python3 -m pytest`. These need CellEngine credentials to run. In
CI, these are provided by GitHub secrets. Locally, you need to set environment
variables:

```sh
CELLENGINE_USERNAME="..."
CELLENGINE_PASSWORD="..."
# for running tests that require S3:
S3_ACCESS_KEY="..."
S3_SECRET_KEY="..."
# Run the integration tests:
python3 -m pytest ./tests/integration/test_integration.py
```

### Conventions

* Error message text should end with a period.
