## Recipes for common operations



from cellengine.utils.api_client.APIClient import APIClient
c = APIClient("gegnew", "^w^A7kpB$2sezF")
exps = c.get_experiments()
e = exps[0]
files = e.fcs_files
f = files[0]
f_again = e.fcs_file(f._id)
f_again_by_name = e.fcs_file(name = f.name)

pops = e.populations
p = e.population(name="my population name")


