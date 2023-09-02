[![image](https://img.shields.io/pypi/v/chemcloud.svg)](https://pypi.python.org/pypi/chemcloud)
[![image](https://img.shields.io/pypi/l/chemcloud.svg)](https://pypi.python.org/pypi/chemcloud)
[![image](https://img.shields.io/pypi/pyversions/chemcloud.svg)](https://pypi.python.org/pypi/chemcloud)
[![Actions status](https://github.com/mtzgroup/chemcloud-client/workflows/Tests/badge.svg)](https://github.com/mtzgroup/chemcloud-client/actions)
[![Actions status](https://github.com/mtzgroup/chemcloud-client/workflows/Basic%20Code%20Quality/badge.svg)](https://github.com/mtzgroup/chemcloud-client/actions)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

Beautiful and user friendly data structures for quantum chemistry.

# chemcloud - A Python Client for ChemCloud

`chemcloud` is a python client for the [ChemCloud Server](https://github.com/mtzgroup/chemcloud-server) that makes performing computational chemistry calculations easy, fast, and fun. All input and output data structures come from [qcio](https://github.com/coltonbh/qcio) for consistency and easy of use and the way calculations are run follows the [qcop](https://github.com/coltonbh/qcop) API. The client provides a simple, yet powerful interface to perform computational chemistry calculation using nothing but modern python and an internet connection.

**Documentation**: <https://mtzgroup.github.io/chemcloud-client>

**Source Code**: <https://github.com/mtzgroup/chemcloud-client>

## Requirements

- Python 3.8++

## Installation

```sh
pip install chemcloud
```

## Usage

- Create a ChemCloud account at [https://chemcloud.mtzlab.com/signup](https://chemcloud.mtzlab.com/signup) (or the address of the ChemCloud Server you want to communicate with).
- Instantiate a client
- Configure client (only required the very first time you use `CCClient`)

```python
>>> from chemcloud import CCClient

>>> client = CCClient()
>>> client.configure() # only run this the very first time you use CCClient
# See supported compute engines on the ChemCloud Server
>>> client.supported_engines
['psi4', 'terachem', ...]
# Test connection to ChemCloud
>>> client.hello_world("Colton")
'Welcome to ChemCloud, Colton'
```

- Create a [Molecule](https://mtzgroup.github.io/chemcloud-client/code_reference/Molecule/).
- `Molecules` can be created opened from `.xyz` files or created in pure python.

```python
>>> from qcio import Molecule
>>> water = Molecule.open("mygeom.xyz")
```

- Specify your compute job using an [ProgramInput](https://mtzgroup.github.io/chemcloud-client/code_reference/AtomicInput/)

```python
>>> from qcio import ProgramInput
>>> prog_inp = ProgramInput(calctype="energy", molecule=water, model={"method": "B3LYP", "basis": "6-31g"}, keywords={})
```

- Submit a computation, specify a target quantum chemistry program, and get back an [SinglePointOutput](https://mtzgroup.github.io/chemcloud-client/code_reference/AtomicResult/) object.

```python
>>> future_result = client.compute("psi4", prog_inp, collect_files=True)
>>> future_result.status
'STARTED'

# Get output
>>> output = future_result.get()
# Successful output
>>> output.success
True
>>> output
SinglePointOutput(...)
# All computed results are stored here
>>> output.results
SinglePointResults(...)

# Failed result
>>> output.success
False
# View output
>>> output
>>> ProgramFailure(...)
# To see error
>>> output.ptraceback
```

- Putting it all together

```python
>>> from chemcloud import CCClient
>>> from qcio import Molecule, ProgramInput

>>> client = CCClient()
>>> water = Molecule.open("mygeom.xyz")
>>> prog_inp = ProgramInput(calctype="energy", molecule=water, model={"method": "B3LYP", "basis": "6-31g"}, keywords={})
>>> future_result = client.compute("psi4", prog_inp)
>>> output = future_result.get()
>>> output
SinglePointOutput(...)
# All computed results are stored here
>>> output.results
SinglePointResults(...)
>>> output.results.return_result
-76.38545794119997
```

### Examples

Examples of various computations can be found in the [documentation](https://mtzgroup.github.io/chemcloud-client/) and in the GiHub repo's [examples directory](https://github.com/mtzgroup/chemcloud-client/tree/main/examples).

## Development

Install [poetry](https://python-poetry.org/)

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

Install the ChemCloud package

```sh
poetry install
```

```sh
sh scripts/tests.sh
```

## Licence

This project is licensed under the terms of the MIT license.
