# Molecule

## Overview

The `Molecule` object is the core representation of a molecule used throughout `tccloud`. The `molecule` object is from the `qcelemental.models` module, but it is available in the `tccloud.models` module for your convenience. You can access the QCElemental documentation on the `Molecule` [here](http://docs.qcarchive.molssi.org/projects/QCElemental/en/stable/model_molecule.html). It is assumed that all geometries are in `bohr`.

## Import the Model object

```python
from tccloud.models import Molecule
```

## Create a Molecule

Molecules can be created directly from data on [pubchem](https://pubchem.ncbi.nlm.nih.gov), a python string, a `psi4` file, an `xyz` file, an `xyz+` file, or a `json` file.

Pubchem:

```python
water = Molecule.from_data("pubchem:water")
```

From Files:

```python
water = Molecule.from_file("water.xyz")
water = Molecule.from_file("water.psi4")
```

## Save a Molecule to a file

```python
water = Molecule.from_data("pubchem:water")
# JSON is the prefered format since it preserves the most information
water.to_file("water.json")
water.to_file("water.xyz")
water.to_file("water.psi4")
```

## Oft-used Attributes

```python
water = Molecule.from_data("pubchem:water")
water.symbols
array(['O', 'H', 'H'], dtype='<U1')water.symbols

water.geometry
array([[ 0.        ,  0.        ,  0.        ],
       [ 0.52421003,  1.68733646,  0.48074633],
       [ 1.14668581, -0.45032174, -1.35474466]])

# All Attributes
attrs = [attr for attr in dir(water) if not attr.startswith("_")]
print(attrs)
```

## Molecule Full Reference

::: tccloud.models:Molecule
