# API Client

The CellEngine `APIClient` object is the low-level interface between the
CellEngine API and entities in the Python SDK. After authenticating, you may
either use the `APIClient` directly or interact with the higher-level SDK
entities.

Assuming you have instantiated the `APIClient` object:
```python
import cellengine
client = cellengine.APIClient("username")
# Password: <enter your password here>
# Alternatively, set CELLENGINE_PASSWORD in your environment
```

then the following sequences of commands are equivalent:

```python
exp = client.get_experiment(name="my experiment")
fcsfile = client.get_fcs_file(experiment_id=exp._id, name="my fcs file")
```

```python
exp = cellengine.Experiment.get(name="my experiment")
fcsfile = cellengine.FcsFile.get(experiment_id=exp._id, name="my fcs file")
```

```python
exp = cellengine.Experiment.get(name="my experiment")
fcsfile = exp.get_fcs_file(name="my fcs file")
```

The `APIClient` provides higher-level [methods](#methods) for interacting with
CellEngine. It also provides `_get`, `_post`, `_patch`, and `_delete` methods
for low-level interaction with the [CellEngine
API](https://docs.cellengine.com/api/). If there is a higher-level feature
that's missing, please feel free to [open an Issue in
GitHub](https://github.com/primitybio/cellengine-python-toolkit/issues).

## Properties
- `base_url` (to override the cellengine.com URL, generally for internal use)
- `username`
- `password`
- `token`
- `user_id`
- `admin`
- `flags`
- `authenticated`
- `cache_info`
- `cache_clear`

## Methods

::: cellengine.APIClient
