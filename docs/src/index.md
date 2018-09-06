# CellEngine API Toolkit for Python

This is the documentation for the Python toolkit for the CellEngine API. For
API documentation visit [here](https://docs.cellengine.com/api/).

## Quickstart
Install `cellengine` using `pip`:

```bash
pip install cellengine
```

For the development version:

```bash
pip install git+https://github.com/primitybio/cellengine-python-toolkit.git
```

### Authentication
```python
import cellengine
client = cellengine.APIClient(username="jason")
# Password: <enter your password here>
# Alternatively, authenticate by setting CELLENGINE_PASSWORD or CELLENGINE_AUTH_TOKEN in your environment

# Get a list of all accessible experiments
experiment = client.get_experiments()

# or get one experiment by its name
experiment = client.get_experiment(name="My experiment")
# alternatively,
experiment = cellengine.Experiment.get(name="My experiment")

# or get one experiment by ID
experiment = client.get_experiment("5f203e852a183003c2459c94")
```

### Get resources:
The following are all equivalent commands, and apply to all resources types:
```python
att = experiment.get_attachment(name="my attachment")
# assuming that 'my attachment' has this ID
att = experiment.get_attachment("5f3ac0ba5465db092213cff5")
att = client.get_attachment(experiment._id, "5f3ac0ba5465db092213cff5")
att = Attachment.get(experiment._id, "my attachment")
```

### Get resources by name or ID
```python
comp = experiment.get_compensation("5f3ac0ba5465db092213cff8")
file = experiment.get_fcs_file(name="160311-96plex-4dye")
```

### Create resources
```python
experiment.create_attachment("my_file.txt")
```

### Update resources
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


## Resources
* [GitHub](https://github.com/PrimityBio/cellengine-python-toolkit/)
* [CellEngine API](https://docs.cellengine.com/api/)
