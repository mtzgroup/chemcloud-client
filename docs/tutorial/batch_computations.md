# Batch Computations

Both single point and geometry optimizations can be performed in bulk by submitting up to 100 computations simultaneously. Simply submit an array of [AtomicInputs][qccloud.models.AtomicInput] or [OptimizationInput][qccloud.models.OptimizationInput] objects as input data.

```python hl_lines="18"
{!../examples/energy_batch.py!}
```
