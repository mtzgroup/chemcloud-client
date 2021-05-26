# Compute

## Overview

Computations are physically executed on [TeraChem Cloud](https://tccloud.mtzlab.com). The `tccloud` python client submits jobs to and retrieves work from TeraChem Cloud. Computations are submitted using the [TCClient][tccloud.client.TCClient] object.

Computations require an [AtomicInput][tccloud.models.AtomicInput] object and the specification of a compute engine.

```python
{!../examples/energy.py!}
```