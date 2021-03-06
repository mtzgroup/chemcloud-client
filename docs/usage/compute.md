# Compute

## Overview

Computations are performed on [TeraChem Cloud](https://tccloud.mtzlab.com). The `tccloud` python client submits jobs to and retrieves from TeraChem Cloud.

Computations require an [AtomicInput](./Atomic Input.md) object and the specification of a compute engine.

```python
>>> from tccloud import TCClient
>>> from tccloud.models import AtomicInput, Molecule

>>> client = TCClient()
>>> water = Molecule.from_data("pubchem:water")
>>> atomic_input = AtomicInput(molecule=water, model={"method": "B3LYP", "basis": "6-31g"}, driver="energy")
>>> future_result = client.compute(atomic_input, engine="terachem_pbs")
>>> result = future_result.get()
>>> result
AtomicResult(driver='energy', model={'method': 'B3LYP', 'basis': '6-31g'}, molecule_hash='b6ec4fa')
>>> result.return_result
-76.38545794119997
```

Supported compute engines can be checked on the client. If you would like to request additional engines please open an [issue](https://github.com/mtzgroup/tccloud/issues).

```python
>>> client.supported_engines
['psi4', 'terachem_pbs', ...]
```

## Keywords

Keywords specific to a quantum chemistry engine can be added to an [AtomicInput](./Atomic Input.md) as follows:

```python
ai = AtomicInput(
    ...,
    keywords={
        "molden": True,
        "imd_orbital_type": "whole_c",
        ...
    }
)

```
