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
```python
pip install cellengine
```

Quick start:

#### Authentication
```python
import cellengine
client = cellengine.APIClient(username='your username', password='your password')

experiments = client.experiments
# or:
exp = cellengine.Experiment(name="160311-96plex-4dye")
```

#### API Client

All API methods are implemented on the `APIClient` object. You may retrieve,
update, or delete resources:
```python
experiment = client.get_experiment(name="my experiment")

files = client.get_fcs_files(experiment._id)

plots = client.get_populations(experiment._id)
```

Although most CellEngine API methods are implemented in the `APIClient`, you
may also construct your own requests using the `_get`, `_post`, `_update`, and
`_delete` methods. For instance, to formulate a custom query parameter for
`LIST` routes:
```python
exp_id = client.get_experiment(name="160311-96plex-4dye")._id
# get files with more than 5000 events
files = client._get(f"https://cellengine.com/api/v1/experiments/{exp_id}/fcsfiles",
	params={"query": 'gt(eventCount, 5000)'})
```

Most operations may performed on the `Experiment` object, which has helper
methods for interacting with most other resources. This is the simplest
entry-point for SDK usage.


#### Get resources:
The following are all equivalent commands, and apply to all resources types:
```python
att = [a for a in experiment.attachments if a.name = "my attachment"][0]
att = experiment.get_attachment(name="my attachment")
# assuming that 'my attachment' has this ID
att = experiment.get_attachment("5f3ac0ba5465db092213cff5")
att = client.get_attachment(experiment._id, "5f3ac0ba5465db092213cff5")
att = Attachment.get(experiment._id, "my attachment")
```

#### Get resources by name or ID
```python
comp = experiment.get_compensation("5f3ac0ba5465db092213cff8")
file = experiment.fcs_files(name="160311-96plex-4dye")
```

#### Create resources
```python
experiment.post_attachment("my_file.txt")
```

#### Update resources
```python
att = experiment.get_attachment(name="my_file.txt")
att.filename = "my_new_name.txt"
att.update()
```

#### Operate on resources
```python
file1 = experiment.fcs_files(name="160311-96plex-4dye")
# get a Pandas dataframe of an FcsFile's events, subsampling for only 10 events
events_df = file1.events(preSubsampleN=10)

split_gate = experiment.create_split_gate(
    file1.channels[0], "split_gate", 2300000, 250000
)
# The above command is equivalent to:
split_gate = SplitGate.create(
experiment._id, file1.channels[0], "split_gate", 2300000, 250000
)
```

#### Delete resources
Deleting all resources is final, EXCEPT for
Experiments. Experiments are marked as deleted for 7 days, then
permanently deleted. To undelete an Experiment, use the `.undelete()`
method.
```python
att = experiment.get_attachment(name="my_file.txt")
att.delete()
experiment.attachments  # returns []
```

For more documnentation, refer to the
[Documentation](https://primitybio.github.io/cellengine-python-toolkit/) and
[API Documentation](https://docs.cellengine.com/api/).
