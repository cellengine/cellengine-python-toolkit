## Recipes for common operations

```python
from cellengine.utils.api_client.APIClient import APIClient
client = cellengine.APIClient("username", "password")
e = client.get_experiment(name="my experiment")
fcsfile = e.get_fcs_file(experiment_id=e._id, name="my fcs file")
p = e.get_population(name="my population name")
```
