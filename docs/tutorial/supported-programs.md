Supported compute engines in chemcloud can be checked as follows:

```python
from chemcloud import CCClient

client = CCClient()
client.supported_engines
["psi4", "terachem_fe", "rdkit", ...]
```

Please see [BigChem Algorithms](https://github.com/mtzgroup/chemcloud-client/blob/main/docs/tutorial/bigchem_algorithms.md) for details on parallel execution algorithms unique to the BigChem compute engine.
