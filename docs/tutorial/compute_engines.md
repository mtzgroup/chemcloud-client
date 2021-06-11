# Compute Engines

Supported compute engines in `tccloud` can be checked as follows:

```python
from tccloud import TCClient

client = TCClient()
client.supported_engines
["psi4", "terachem_pbs", "rdkit", ...]
```

Please see [TeraChem Cloud Algorithms](./terachem_cloud_algorithms.md) for details on parallel execution algorithms unique to the TeraChem Cloud (`tcc`) compute engine.

## Keywords

Keywords specific to a quantum chemistry engine can be added to an [AtomicInput][tccloud.models.AtomicInput] as follows:

```python
ai = AtomicInput(
    ...,
    keywords={
        "molden": True,
        "restricted": True,
        ...
    }
)

```

## TeraChem

### Relevant keywords

| Keyword      | Type    | Description                                                                                                                   | Default Value |
| :----------- | :------ | :---------------------------------------------------------------------------------------------------------------------------- | :------------ |
| `molden`     | `bool`  | If `True` with `mo_ouput=True` the `result.extras["molden"]` field will contain a string of the molden file                   | `False`       |
| `mo_output`  | `bool`  | Request atomic orbital and molecular orbital information. Needs to be set to `True` to generate data required for molden file | `False`       |
| `convthre`   | `float` | Convergence threshold for SCF calculations                                                                                    | `3.0e-5`      |
| `precision`  | `str`   | Can be `single`, `double`, `mixed` or other values                                                                            | `Unknown`     |
| `dftgrid`    | `int`   | Speeds up a computation somehow. `0` makes things quicker                                                                     | `Unknown`     |
| `restricted` | `bool`  | Restricted computation                                                                                                        | `True`        |
| `closed`     | `bool`  | Closed shell                                                                                                                  | `True`        |

## Psi4

## rdkit

## xtb

xtb specific documentation on how to run calculations using the [QCSchema](https://molssi-qc-schema.readthedocs.io/en/latest/index.html) specification used TeraChem Cloud can be found [here](https://xtb-python.readthedocs.io/en/latest/qcarchive.html?highlight=run_qcschema) and [here](https://xtb-python.readthedocs.io/en/latest/_modules/xtb/qcschema/harness.html).
