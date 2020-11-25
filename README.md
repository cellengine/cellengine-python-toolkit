![Lint](https://github.com/primitybio/cellengine-python-toolkit/workflows/Lint/badge.svg)
![Test](https://github.com/primitybio/cellengine-python-toolkit/workflows/Test/badge.svg)
[![codecov](https://codecov.io/gh/primitybio/cellengine-python-toolkit/branch/master/graph/badge.svg)](https://codecov.io/gh/primitybio/cellengine-python-toolkit)

CellEngine Python API Toolkit
-----

A Python wrapper around the CellEngine API that enables you to securely,
reproducibly and easily interact with your data from a Python or Jupyter
environment.

[Python Toolkit Documentation](https://primitybio.github.io/cellengine-python-toolkit/)

[CellEngine API Documentation](https://docs.cellengine.com/api/)

## Installing:
```bash
pip install cellengine
```

#### Quick start:
Please see the [documentation](https://primitybio.github.io/cellengine-python-toolkit/) for a quick-start and recipes for use of the toolkit.

```python
client = cellengine.APIClient(username="jason")
# Password: <enter your password here>

experiment = client.get_experiments()
```

#### API Client

All API methods are implemented on the `APIClient` object. You can retrieve,
update, or delete resources:
```python
experiment = client.get_experiment(name="my experiment")
files = client.get_fcs_files(experiment._id)
```

Most operations may be performed on the `Experiment` object, which has helper
methods for interacting with most other resources. This is the simplest
way to use the API.
See the [docs](https://primitybio.github.io/cellengine-python-toolkit/experiments/) for more information.
