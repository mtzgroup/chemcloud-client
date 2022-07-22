# chemcloud - A Python Client for ChemCloud

`chemcloud` is a python client for the [ChemCloud Server](https://github.com/mtzgroup/chemcloud-server) that makes performing computational chemistry calculations easy, fast, and fun. All input and output data structures are based on the [QCSchema](https://molssi-qc-schema.readthedocs.io/en/latest/index.html#) specification designed by [The Molecular Sciences Software Institute](https://molssi.org). The client provides a simple, yet powerful interface to perform computational chemistry calculation using nothing but modern python and an internet connection.

**Documentation**: <https://mtzgroup.github.io/chemcloud-client>

**Source Code**: <https://github.com/mtzgroup/chemcloud-client>

## Requirements

- Python 3.7+
- `chemcloud` stands on the shoulders of giants. It internally depends upon [QCElemental](http://docs.qcarchive.molssi.org/projects/QCElemental/en/stable/), [httpx](https://www.python-httpx.org), and [toml](https://pypi.org/project/toml/).
- The `AtomicInput`, `Molecule`, `Model`, and `AtomicResult` models used throughout the package come directly from [QCElemental](http://docs.qcarchive.molssi.org/projects/QCElemental/en/stable/). They are included in `chemcloud.models` for your convenience.

## Installation

```sh
pip install chemcloud
```

## Usage

- Create a ChemCloud account at [https://chemcloud.mtzlab.com/signup](https://chemcloud.mtzlab.com/signup) (or wherever a ChemCloud Server is running)
- Instantiate a client
- Configure client (only required the very first time you use `CCClient`)

```python
>>> from chemcloud import CCClient

>>> client = CCClient()
>>> client.configure() # only run this the very first time you use CCClient
# See supported compute engines on the ChemCloud Server
>>> client.supported_engines
['psi4', 'terachem_fe', ...]
# Test connection to ChemCloud
>>> client.hello_world("Colton")
'Welcome to ChemCloud, Colton'
```

- Create a [Molecule](https://mtzgroup.github.io/chemcloud-client/code_reference/Molecule/).
- `Molecules` can be created from [pubchem](https://pubchem.ncbi.nlm.nih.gov), local files such as `.xyz` or `.psi4` files, or using pure python.

```python
>>> from chemcloud.models import Molecule
>>> water = Molecule.from_data("pubchem:water")
```

- Specify your compute job using an [AtomicInput](https://mtzgroup.github.io/chemcloud-client/code_reference/AtomicInput/)

```python
>>> from chemcloud.models import AtomicInput
>>> atomic_input = AtomicInput(molecule=water, model={"method": "B3LYP", "basis": "6-31g"}, driver="energy")
```

- Submit a computation, specify a target quantum chemistry engine, and get back an [AtomicResult](https://mtzgroup.github.io/chemcloud-client/code_reference/AtomicResult/)

```python
>>> future_result = client.compute(atomic_input, engine="terachem_fe")
>>> future_result.status
'STARTED'

# Get result
>>> result = future_result.get()
# Successful result
>>> result.success
True
>>> result
AtomicResult(driver='energy', model={'method': 'B3LYP', 'basis': '6-31g'}, molecule_hash='b6ec4fa')
>>> result.return_result
-76.38545794119997

# Failed result
>>> result.success
False
# View result
>>> result
>>> FailedOperation(error=ComputeError(error_type='input_error', error_message='QCEngine Input Error: Traceback (most recent call last):...'))
>>> from pprint import pprint
>>> pprint(result.error.error_message)
```

- Putting it all together

```python
>>> from chemcloud import CCClient
>>> from chemcloud.models import AtomicInput, Molecule

>>> client = CCClient()
>>> water = Molecule.from_data("pubchem:water")
>>> atomic_input = AtomicInput(molecule=water, model={"method": "B3LYP", "basis": "6-31g"}, driver="energy")
>>> future_result = client.compute(atomic_input, engine="terachem_fe")
>>> result = future_result.get()
>>> result
AtomicResult(driver='energy', model={'method': 'B3LYP', 'basis': '6-31g'}, molecule_hash='b6ec4fa')
>>> result.return_result
-76.38545794119997
```

### Examples

Examples of various computations can be found in the [documentation](https://mtzgroup.github.io/chemcloud-client/) and in the GiHub repo's [examples directory](https://github.com/mtzgroup/chemcloud-client/tree/main/examples).

## Development

Create and source a virtual environment using python 3.7+

```sh
python -m venv env
source ./env/bin/activate
```

Install flit

```sh
python -m pip install flit
```

Install `chemcloud` package and its dependencies

```sh
flit install --deps develop --symlink
```

Run tests to check install

```sh
pytest
```

## Licence

This project is licensed under the terms of the MIT license.
