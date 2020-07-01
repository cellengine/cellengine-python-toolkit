## Recipes for common operations

```python
from cellengine.utils.api_client.APIClient import APIClient
client = cellengine.APIClient("username", "password")
e = client.get_experiment(name="my experiment")
fcsfile = client.get_fcsfile(experiment_id=e._id, name="my fcs file")

pops = e.populations
p = e.get_population(name="my population name")
```
