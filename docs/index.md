# CellEngine API Toolkit for Python

This is the documentation for the Python toolkit for the CellEngine API. For
API documentation visit [here](https://docs.cellengine.com/api/).

## Quick Start
Install `cellengine` using `pip` from GitHub:

```bash
pip install git+https://github.com/cellengine/cellengine-python-toolkit.git
```

### Authentication
```python
import cellengine
client = cellengine.APIClient(username="jason")
# Password: <enter your password here>
# Alternatively, authenticate by setting CELLENGINE_PASSWORD or 
# CELLENGINE_AUTH_TOKEN in your environment

# Get a list of all accessible experiments
experiments = client.get_experiments()
```

### Get resources
All resources have a unique ID stored as `_id`, e.g. `Experiment()._id`.
Resources can be retrieved by name or by ID:
```python
# Get an experiment by its name
experiment = client.get_experiment(name="My experiment")
experiment = cellengine.Experiment.get(name="My experiment")
# or by its ID
experiment = client.get_experiment("5f203e852a183003c2459c94")
```
```py
# Get an attachment by name
att = experiment.get_attachment(name="my attachment")
att = Attachment.get(experiment._id, "my attachment")
# or by its ID
att = experiment.get_attachment("5f3ac0ba5465db092213cff5")
att = client.get_attachment(experiment._id, "5f3ac0ba5465db092213cff5")
```

### Create resources
```python
experiment.upload_attachment("path/to/my_file.txt")
experiment.create_compensation("My comp", ["Chan1", "Chan2"], [1, 0.1, 0, 1])
```

### Update resources
```python
att = experiment.get_attachment(name="my_file.txt")
att.filename = "my_new_name.txt"
att.update()  # save changes back to CellEngine
```

### Operate on resources
```python
file1 = experiment.get_fcs_file(name="160311-96plex-4dye")
# Get a Pandas dataframe containing an FcsFile's events, subsampled to 10 events
events_df = file1.get_events(preSubsampleN=10)
```

### Delete resources
Deleting all resources is final, except for Experiments, Folders and FCS files.
Those resources are marked as deleted, then permanently deleted at a later date.
To undelete an Experiment, use the `.undelete()` method.

```python
att = experiment.get_attachment(name="my_file.txt")
att.delete()
experiment.attachments  # returns []
```

## More Help
* [GitHub Issues](https://github.com/cellengine/cellengine-python-toolkit/issues)
* [CellEngine API](https://docs.cellengine.com/api/)
