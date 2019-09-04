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


