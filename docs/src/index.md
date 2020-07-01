# CellEngine API Toolkit for Python

For full API documentation visit [CellEngine](https://docs.cellengine.com/api/).

## Quickstart

Install `cellengine-python-toolkit` using `pip`:

```bash
$ pip install cellengine-python-toolkit
```

For the development version:

```bash
$ pip install git+https://github.com/primitybio/cellengine-python-toolkit.git
```

```python
  import cellengine
  client = cellengine.APIClient(username="jason")
  # password will be prompted
  experiment = client.get_experiment(name="My experiment")
```

## Resources
* [GitHub](https://github.com/PrimityBio/cellengine-python-toolkit/)
* [CellEngine API](https://docs.cellengine.com/api/)
