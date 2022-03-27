# TeraChem Cloud Algorithms

TeraChem Cloud implements some of its own concurrent algorithms that leverage its horizontally scalable backend infrastructure. These include a parallel hessian algorithm and parallel frequency analysis algorithm. To use them submit either a `hessian` or `properties` computation to TeraChem Cloud using `tcc` as the engine. Keywords specific to these algorithms are added to `.extras['tcc:keywords']`. None are required and all are optional.

## Hessian

```python
{!../examples/parallel_hessian.py!}
```

## Frequency Analysis

```python
{!../examples/parallel_frequency_analysis.py!}
```

## Keywords

Keywords are passed in `AtomicInput.extras['tcc:keywords']`.

| Keyword           | Type    | Description                                                 | Default Value  |
| :---------------- | :------ | :---------------------------------------------------------- | :------------- |
| `gradient_engine` | `str`   | The program to use for gradient calculations                | `terachem_pbs` |
| `dh`              | `float` | Displacement for gradient geometries for finite difference  | `5.0e-3`       |
| `energy`          | `float` | Electronic energy passed to the harmonic free energy module | `0.0`          |
| `temperature`     | `float` | Temperature passed to the harmonic free energy module       | `300.0`        |
| `pressure`        | `float` | Pressure passed to the harmonic free energy module          | `1.0`          |
