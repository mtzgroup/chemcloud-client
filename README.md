# tccloud - A Python Client for TeraChem Cloud

`tccloud` is a python package that provides an easy interface to the TeraChem Cloud web service. All input and output data structures are based on the [QCSchema](https://molssi-qc-schema.readthedocs.io/en/latest/index.html#) specification designed by [The Molecular Sciences Software Institute](https://molssi.org) as implemented in their [QCElemental](http://docs.qcarchive.molssi.org/projects/QCElemental/en/stable/) package. This enables common and well defined input/output data structures to be used to power a whole suite of Quantum Chemistry packages.

## Requirements

- Python 3.6+
- `tccloud` stands on the shoulders of giants. It internally depends upon [QCElemental](http://docs.qcarchive.molssi.org/projects/QCElemental/en/stable/), [httpx](https://www.python-httpx.org), and [toml](https://pypi.org/project/toml/).
- The `AtomicInput`, `Molecule`, `Model`, and `AtomicResult` models used throughout the package come directly from [QCElemental](http://docs.qcarchive.molssi.org/projects/QCElemental/en/stable/). They are included in `tccloud.models` for your convenience.

## Installation

```sh
pip install tccloud
```

## Example

### The Absolute Minimum

- Create an account at https://tcc.mtzlab.com/signup
- Instantiate a client
- Configure client (only required the very first time you use `TCClient`)

```python
from tccloud import TCClient

client = TCClient()
client.configure()
```

- Create a `Molecule`
- More details about the `Molecule` object can be found [here](http://docs.qcarchive.molssi.org/en/latest/basic_examples/QCElemental.html#Molecule-Parsing-and-Models) and [here](http://docs.qcarchive.molssi.org/projects/QCElemental/en/stable/model_molecule.html). `Molecules` can be instantiated using data from [pubchem](https://pubchem.ncbi.nlm.nih.gov), local files, or using only python.

```python
from tccloud.models import Molecule
water = Molecule.from_data("pubchem:water")
```

- Specify your model and driver

```python
from tccloud.models import Model
model = Model(method="B3LYP", basis="6-31g")
driver = "energy"
```

- Create an `AtomicInput` object that defines the desired computation
- More details about the `AtomicInput` object can be found [here](http://docs.qcarchive.molssi.org/projects/QCElemental/en/stable/model_result.html).

```python
atomic_input = AtomicInput(molecule=water, model=model, driver=driver)
```

- Submit computation, specify a target quantum chemistry engine, and get an [AtomicResult](http://docs.qcarchive.molssi.org/projects/QCElemental/en/stable/model_result.html)

```python
future_result = client.compute(atomic_input, engine="psi4")
result = future_result.get()
```

- Putting it all together

```python
from tccloud import TCClient
from tccloud.models import AtomicInput, Model, Molecule

client = TCClient()
client.configure() # only run the very first time you use TCClient
water = Molecule.from_data("pubchem:water")
model = Model(method="B3LYP", basis="6-31g")
driver = "energy"
atomic_input = AtomicInput(molecule=water, model=model, driver=driver)
future_result = client.compute(atomic_input, engine="psi4")
result = future_result.get()

```

## Licence

This project is licensed under the terms of the MIT license.
