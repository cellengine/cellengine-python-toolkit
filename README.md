[![CircleCI](https://circleci.com/gh/primitybio/cellengine-python-toolkit/tree/master.svg?style=svg&circle-token=759714479ab360ce3fda49fa8658d02df8164d0a)](https://circleci.com/gh/primitybio/cellengine-python-toolkit/tree/master)

CellEngine Python API Toolkit
-----

Installing:
```
pip install cellengine
```

Quick start:

```
import cellengine
client = cellengine.Client(username='gegnew', password='testpass1')

experiments = client.experiments
# or:
exp = cellengine.Experiment(name="160311-96plex-4dye")
```

### Import new experiments:
# TODO

List resources:
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
