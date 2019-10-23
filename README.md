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

##Developer Notes
- `id` is a python builtin, which causes some confusion. We use `_id` to indicate
the ID of an API object, but the `attrs` package does not accept leading
underscores as a keyword argument. In other words, an init arg `_id = attr.ib()` in a
class must be passed to instantiate that class as `id`. In every other case,
the variable `_id` should be used. Practically, this means:
    - pass `_id` to functions that take an ID as an argument. This is the only
      situation a user should encounter.
    - pass `id` instead of `_id` to `attrs` classes when instantiating them.
      This should only happen inside the SDK; a user should never have to pass
      `id` instead of `_id`.
    - pass `properties` instead of `_properties` to `attrs` classes when
      instantiating them. A user should probably never have to pass
      `_properties` at all; this should be managed behind the scenes.

