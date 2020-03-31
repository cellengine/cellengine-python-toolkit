# CellEngine API Toolkit for Python

For full API documentation visit [CellEngine](https://docs.cellengine.com/api/).

## Quickstart

Install `cellengine` using `pip`:

```bash
$ pip install git+https://github.com/primitybio/cellengine-python-toolkit.git
```

```python
  import cellengine
  client = cellengine.Client(username="jason")
  # password will be prompted
  experiment = client.get_experiment("My experiment")
```

## Resources
* [GitHub](https://github.com/PrimityBio/cellengine-python-toolkit/)
* [API documentation](https://docs.cellengine.com/api/)
