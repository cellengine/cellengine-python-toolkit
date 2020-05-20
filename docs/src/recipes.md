## Recipes for common operations



from cellengine.utils.api_client.APIClient import APIClient
c = APIClient("gegnew", "^w^A7kpB$2sezF")
exps = c.get_experiments()
e = exps[0]
files = e.fcsfiles
f = files[0]
f_again = e.fcsfile(f._id)
f_again_by_name = e.fcsfile(name = f.name)

pops = e.populations
p = e.population(name="my population name")


