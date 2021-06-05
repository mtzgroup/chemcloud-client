# Geometry Optimization

## Basic Working Example

- Create a Molecule
- Define parameters for the compute engine
- Define the optimization parameters for the optimizer and specify the compute engine
- Specify the optimizer to run

```Python hl_lines="8 10-14 21 24 29"
{!../examples/optimization.py!}
```

## Using Force Fields

`rdkit` can be specified as a compute backend to perform optimizations using force field methods instead of quantum chemistry backends. To use `rdkit` force field methods simply modify the model specification and `program` specification as shown below. Also note that `rdkit` requires the molecular connectivity to be defined.

```python
# Hack to quickly drop in water's connectivity
water = Molecule.from_data("pubchem:water")
water = Molecule(**{**water.dict(), "connectivity": [(0, 1, 1.0), (0, 2, 1.0)]})

input_spec = QCInputSpecification(
    ...
    model = {"method": "UFF"} # or any other force field
)

opt_input = OptimizationInput(
    ...
    keywords={"program": "rdkit"},
)

future_result = client.compute_procedure(opt_input, "geometric")

```

## Berny Specifics

The `berny` procedure uses the [pyberny](https://github.com/jhrmnn/pyberny) package to perform a geometry optimization. `berny` specific keywords are subject to change as the `berny` package evolves, but for simplicity a short list is included here with default values noted:

| Keyword        | Description                                                             | Default Value |
| :------------- | :---------------------------------------------------------------------- | :------------ |
| `maxsteps`     | Maximum number of steps in the optimization                             | `100`         |
| `gradientmax`  | Convergence criteria (AU)                                               | `0.45e-3`     |
| `gradientrms`  | Convergence criteria (AU)                                               | `0.15e-3`     |
| `stepmax`      | Step in internal coordinates, assuming radian units for angles (AU)     | `1.8e-3`      |
| `steprms`      | Step in internal coordinates, assuming radian units for angles (AU)     | `0.45e-3`     |
| `trust`        | Initial trust radius in AU. It is the maximum RMS of the quadratic step | `0.3`         |
| `dihedral`     | Form dihedral angles                                                    | `True`        |
| `superweakdih` | Form dihedral angles containing two or more noncovalent bonds           | `False`       |

## geomeTRIC Specifics

The `geometric` procedure uses the [geomeTRIC](https://github.com/leeping/geomeTRIC) package to perform a geometry optimization. `geomeTRIC` specific keywords are subject to change as the `geomeTRIC` package evolves. Since `geomeTRIC` has considerably more keywords, here's the source code that defines varous parameters for an optimization. Keywords noted below can be included in the `OptimizationInput` keywords dictionary. If these options are overwhelming, keep in mind you can run both the `berny` and `geometric` optimizers without any keywords and the optimizers will use sensible defaults.

```python
class OptParams(object):
    """
    Container for optimization parameters.
    The parameters used to be contained in the command-line "args",
    but this was dropped in order to call Optimize() from another script.
    """
    def __init__(self, **kwargs):
        # Whether we are optimizing for a transition state. This changes a number of default parameters.
        self.transition = kwargs.get('transition', False)
        # CI optimizations sometimes require tiny steps
        self.meci = kwargs.get('meci', False)
        # Handle convergence criteria; this edits the kwargs
        self.convergence_criteria(**kwargs)
        # Threshold (in a.u. / rad) for activating alternative algorithm that enforces precise constraint satisfaction
        self.enforce = kwargs.get('enforce', 0.0)
        # Small eigenvalue threshold
        self.epsilon = kwargs.get('epsilon', 1e-5)
        # Interval for checking the coordinate system for changes
        self.check = kwargs.get('check', 0)
        # More verbose printout
        self.verbose = kwargs.get('verbose', False)
        # Starting value of the trust radius
        # Because TS optimization is experimental, use conservative trust radii
        self.trust = kwargs.get('trust', 0.01 if self.transition else 0.1)
        # Maximum value of trust radius
        self.tmax = kwargs.get('tmax', 0.03 if self.transition else 0.3)
        # Minimum value of the trust radius
        self.tmin = kwargs.get('tmin', 0.0 if (self.transition or self.meci) else min(1.2e-3, self.Convergence_drms))
        # Minimum size of a step that can be rejected
        self.thre_rj = kwargs.get('thre_rj', 1e-4 if (self.transition or self.meci) else 1e-2)
        # Sanity checks on trust radius
        if self.tmax < self.tmin:
            raise ParamError("Max trust radius must be larger than min")
        # The trust radius should not be outside (tmin, tmax)
        self.trust = min(self.tmax, self.trust)
        self.trust = max(self.tmin, self.trust)
        # Maximum number of optimization cycles
        self.maxiter = kwargs.get('maxiter', 300)
        # Use updated constraint algorithm implemented 2019-03-20
        self.conmethod = kwargs.get('conmethod', 0)
        # Write Hessian matrix at optimized structure to text file
        self.write_cart_hess = kwargs.get('write_cart_hess', None)
        # Output .xyz file name may be set separately in
        # run_optimizer() prior to calling Optimize().
        self.xyzout = kwargs.get('xyzout', None)
        # Name of the qdata.txt file to be written.
        # The CLI is designed so the user passes true/false instead of the file name.
        self.qdata = 'qdata.txt' if kwargs.get('qdata', False) else None
        # Whether to calculate or read a Hessian matrix.
        self.hessian = kwargs.get('hessian', None)
        if self.hessian is None:
            # Default is to calculate Hessian in the first step if searching for a transition state.
            # Otherwise the default is to never calculate the Hessian.
            if self.transition: self.hessian = 'first'
            else: self.hessian = 'never'
        if self.hessian.startswith('file:'):
            if os.path.exists(self.hessian[5:]):
                # If a path is provided for reading a Hessian file, read it now.
                self.hess_data = np.loadtxt(self.hessian[5:])
            else:
                raise IOError("No Hessian data file found at %s" % self.hessian)
        elif self.hessian.lower() in ['never', 'first', 'each', 'stop', 'last', 'first+last']:
            self.hessian = self.hessian.lower()
        else:
            raise RuntimeError("Hessian command line argument can only be never, first, last, first+last, each, stop, or file:<path>")
        # Perform a frequency analysis whenever a cartesian Hessian is computed
        self.frequency = kwargs.get('frequency', None)
        if self.frequency is None: self.frequency = True
        # Temperature and pressure for harmonic free energy
        self.temperature, self.pressure = kwargs.get('thermo', [300.0, 1.0])
        # Number of desired samples from Wigner distribution
        self.wigner = kwargs.get('wigner', 0)
        if self.wigner and not self.frequency:
            raise ParamError('Wigner sampling requires frequency analysis')
        # Reset Hessian to guess whenever eigenvalues drop below epsilon
        self.reset = kwargs.get('reset', None)
        if self.reset is None: self.reset = not (self.transition or self.meci or self.hessian == 'each')
```

And convergence criteria:

```python
def convergence_criteria(self, **kwargs):
        criteria = kwargs.get('converge', [])
        if len(criteria)%2 != 0:
            raise RuntimeError('Please pass an even number of options to --converge')
        for i in range(int(len(criteria)/2)):
            key = 'convergence_' + criteria[2*i].lower()
            try:
                val = float(criteria[2*i+1])
                logger.info('Using convergence criteria: %s %.2e\n' % (key, val))
            except ValueError:
                # This must be a set
                val = str(criteria[2*i+1])
                logger.info('Using convergence criteria set: %s %s\n' % (key, val))
            kwargs[key] = val
        # convergence dictionary to store criteria stored in order of energy, grms, gmax, drms, dmax
        # 'GAU' contains the default convergence criteria that are used when nothing is passed.
        convergence_sets = {'GAU': [1e-6, 3e-4, 4.5e-4, 1.2e-3, 1.8e-3],
                            'NWCHEM_LOOSE': [1e-6, 3e-3, 4.5e-3, 3.6e-3, 5.4e-3],
                            'GAU_LOOSE': [1e-6, 1.7e-3, 2.5e-3, 6.7e-3, 1e-2],
                            'TURBOMOLE': [1e-6, 5e-4, 1e-3, 5.0e-4, 1e-3],
                            'INTERFRAG_TIGHT': [1e-6, 1e-5, 1.5e-5, 4.0e-4, 6.0e-4],
                            'GAU_TIGHT': [1e-6, 1e-5, 1.5e-5, 4e-5, 6e-5],
                            'GAU_VERYTIGHT': [1e-6, 1e-6, 2e-6, 4e-6, 6e-6]}
        # Q-Chem style convergence criteria (i.e. gradient and either energy or displacement)
        self.qccnv = kwargs.get('qccnv', False)
        # Molpro style convergence criteria (i.e. gradient and either energy or displacement, with different defaults)
        self.molcnv = kwargs.get('molcnv', False)
        # Check if there is a convergence set passed else use the default
        set_name = kwargs.get('convergence_set', 'GAU').upper()
        # If we have extra keywords apply them here else use the set
        # Convergence criteria in a.u. and Angstrom
        self.Convergence_energy = kwargs.get('convergence_energy', convergence_sets[set_name][0])
        self.Convergence_grms = kwargs.get('convergence_grms', convergence_sets[set_name][1])
        self.Convergence_gmax = kwargs.get('convergence_gmax', convergence_sets[set_name][2])
        self.Convergence_drms = kwargs.get('convergence_drms', convergence_sets[set_name][3])
        self.Convergence_dmax = kwargs.get('convergence_dmax', convergence_sets[set_name][4])
        # Convergence criteria that are only used if molconv is set to True
        self.Convergence_molpro_gmax = kwargs.get('convergence_molpro_gmax', 3e-4)
        self.Convergence_molpro_dmax = kwargs.get('convergence_molpro_dmax', 1.2e-3)
```
