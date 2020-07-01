[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Lint](https://github.com/primitybio/cellengine-python-toolkit/workflows/Lint/badge.svg)
![Test](https://github.com/primitybio/cellengine-python-toolkit/workflows/Test/badge.svg)
[![codecov](https://codecov.io/gh/primitybio/cellengine-python-toolkit/branch/master/graph/badge.svg)](https://codecov.io/gh/primitybio/cellengine-python-toolkit)

CellEngine Python API Toolkit
-----

A Python wrapper around the CellEngine API that enables you to securely,
reproducibly and easily interact with your data from a Python or Jupyter
environment.

[Documentation](https://primitybio.github.io/cellengine-python-toolkit/)

[API Documentation](https://docs.cellengine.com/api/)


## Installing:
```
pip install cellengine
```

Quick start:

Most operations are performed on the `Experiment` object. 

#### Authentication
```
import cellengine
client = cellengine.Client(username='your username', password='your password')

experiments = client.experiments
# or:
exp = cellengine.Experiment(name="160311-96plex-4dye")
```

#### List resources:
```
experiment.files
experiment.populations
experiment.compensations
experiment.gates
```

### Create a complex population
There must already be a gate to base the population on.
```
# TODO
exp.create_complex_population()
```
