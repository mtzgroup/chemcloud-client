# Compute

## Overview

Computations are physically executed on [ChemCloud](https://chemcloud.mtzlab.com). The `chemcloud` python client submits jobs to and retrieves work from ChemCloud. Computations are submitted using the [CCClient][chemcloud.client.CCClient] object.

Computations require an [AtomicInput][chemcloud.models.AtomicInput] object and the specification of a compute engine.

```python
{!../examples/energy.py!}
```
