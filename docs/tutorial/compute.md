# Compute

## Overview

Computations are physically executed on [TeraChem Cloud](https://tccloud.mtzlab.com). The `tccloud` python client submits jobs to and retrieves work from TeraChem Cloud. Computations are submitted using the [TCClient][tccloud.client.TCClient] object.

Computations require an [AtomicInput][tccloud.models.AtomicInput] object and the specification of a compute engine.

```python
{!../examples/energy.py!}
```

Supported compute engines can be checked on the client. If you would like to request additional engines please open an [issue](https://github.com/mtzgroup/tccloud/issues).

```python
>>> client.supported_engines
['psi4', 'terachem_pbs', ...]
```

## Keywords

Keywords specific to a quantum chemistry engine can be added to an [AtomicInput][tccloud.models.AtomicInput] as follows:

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
