# Compute

Computations are physically executed by a BigChem instance fronted by a ChemCloud server. The chemcloud python client submits jobs to and retrieves work from the ChemCloud server. Computations are submitted using the [CCClient][chemcloud.client.CCClient] object.

Computations require a QC proram and `ProgramInput` or `DualProgramInput` object. The `ProgramInput` object contains all the information necessary to run a single calculation. The `DualProgramInput` object is used when two QC programs are used in tandem, such as when performing a geometry optimization with one program that uses a subprogram for the energy and gradient calculations.

## Basic Single Point Calculation

```python
{!../examples/energy.py!}
```

## Including Files in the Input

```python
{!../examples/energy_wfn_input.py!}
```

Files can also be added to an input objects using the `open_file` method.

```python
prog_input.open_file("some_file.dat")
```
