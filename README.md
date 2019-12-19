[![CircleCI](https://circleci.com/gh/primitybio/cellengine-python-toolkit/tree/ge%2Fcircleci.svg?style=svg&circle-token=759714479ab360ce3fda49fa8658d02df8164d0a)](https://circleci.com/gh/primitybio/cellengine-python-toolkit/tree/ge%2Fcircleci)

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
