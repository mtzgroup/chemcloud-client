# BigChem Algorithms

BigChem implements some of its own concurrent algorithms that leverage its horizontally scalable backend infrastructure. These include a parallel hessian algorithm and parallel frequency analysis algorithm. To use them submit a `hessian` calculation to ChemCloud using `bigchem` as the engine. See examples the `parallel_hessian.py` and `parallel_frequency_analysis.py` scripts in the [examples directory](https://github.com/mtzgroup/chemcloud-client/tree/main/examples).

## Parallel Hessian & Frequency Analysis

```python
{!../examples/parallel_hessian.py!}
```

Keywords for the BigChem algorithms:

| Keyword       | Type    | Description                                                | Default Value |
| :------------ | :------ | :--------------------------------------------------------- | :------------ |
| `dh`          | `float` | Displacement for gradient geometries for finite difference | `5.0e-3`      |
| `temperature` | `float` | Temperature passed to the harmonic free energy module      | `300.0`       |
| `pressure`    | `float` | Pressure passed to the harmonic free energy module         | `1.0`         |
