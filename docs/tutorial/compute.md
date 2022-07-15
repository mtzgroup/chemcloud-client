# Compute

## Overview

Computations are physically executed on [QC Cloud](https://qccloud.mtzlab.com). The `qccloud` python client submits jobs to and retrieves work from QC Cloud. Computations are submitted using the [QCClient][qccloud.client.qcclient] object.

Computations require an [AtomicInput][qccloud.models.atomicinput] object and the specification of a compute engine.

```python
{!../examples/energy.py!}
```
