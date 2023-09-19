[![image](https://img.shields.io/pypi/v/chemcloud.svg)](https://pypi.python.org/pypi/chemcloud)
[![image](https://img.shields.io/pypi/l/chemcloud.svg)](https://pypi.python.org/pypi/chemcloud)
[![image](https://img.shields.io/pypi/pyversions/chemcloud.svg)](https://pypi.python.org/pypi/chemcloud)
[![Actions status](https://github.com/mtzgroup/chemcloud-client/workflows/Tests/badge.svg)](https://github.com/mtzgroup/chemcloud-client/actions)
[![Actions status](https://github.com/mtzgroup/chemcloud-client/workflows/Basic%20Code%20Quality/badge.svg)](https://github.com/mtzgroup/chemcloud-client/actions)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

# chemcloud - A Python Client for ChemCloud

`chemcloud` is a python client for the [ChemCloud Server](https://github.com/mtzgroup/chemcloud-server). A ChemCloud server securely exposes a [BigChem](https://github.com/mtzgroup/bigchem) compute system over the open internet. All input and output data structures come from [qcio](https://github.com/coltonbh/qcio) and using the ChemCloud client looks almost identical to using the [qcop](https://github.com/coltonbh/qcop) library except that calculations are performed on a remote machine rather than the end user's machine. The client provides a simple, yet powerful interface to perform computational chemistry calculation using nothing but modern python and an internet connection.

**Documentation**: <https://mtzgroup.github.io/chemcloud-client>

`chemcloud` works in harmony with a suite of other quantum chemistry tools for fast, structured, and interoperable quantum chemistry.

## The QC Suite of Programs

- [qcio](https://github.com/coltonbh/qcio) - Beautiful and user friendly data structures for quantum chemistry.
- [qcparse](https://github.com/coltonbh/qcparse) - A library for efficient parsing of quantum chemistry data into structured `qcio` objects.
- [qcop](https://github.com/coltonbh/qcop) - A package for operating quantum chemistry programs using `qcio` standardized data structures. Compatible with `TeraChem`, `psi4`, `QChem`, `NWChem`, `ORCA`, `Molpro`, `geomeTRIC` and many more.
- [BigChem](https://github.com/mtzgroup/bigchem) - A distributed application for running quantum chemistry calculations at scale across clusters of computers or the cloud. Bring multi-node scaling to your favorite quantum chemistry program.
- `ChemCloud` - A [web application](https://github.com/mtzgroup/chemcloud-server) and associated [Python client](https://github.com/mtzgroup/chemcloud-client) for exposing a BigChem cluster securely over the internet.

## Installation

```sh
pip install chemcloud
```

## Quickstart

- Create a ChemCloud account at [https://chemcloud.mtzlab.com/signup](https://chemcloud.mtzlab.com/signup) (or the address of the ChemCloud Server you want to communicate with).
- Instantiate a client
- Configure client (only required the very first time you use `CCClient`)
- Run calculations

```python
from chemcloud import CCClient

client = CCClient()
client.configure() # only run this the very first time you use CCClient
# See supported compute engines on the ChemCloud Server
client.supported_engines
['psi4', 'terachem', ...]
# Test connection to ChemCloud
client.hello_world("Colton")
'Welcome to ChemCloud, Colton'
```

- Perform calculations just like you would with `qcop` except calling `client.compute` instead of `qcop.compute`. Rather than getting back an `Output` object directly, `client.compute` returns a `FutureResult` object which can be used to get the output of the computation once it is complete.

```python
from qcio import Molecule, ProgramInput
# Create the molecule
h2o = Molecule.open("h2o.xyz")

# Define the program input
prog_input = ProgramInput(
    molecule=h2o,
    calctype="energy",
    model={"method": "hf", "basis": "sto-3g"},
    keywords={"purify": "no", "restricted": False},
)

# Submit the calculation to the server
future_output = client.compute("terachem", prog_input, collect_files=True)

# Status can be checked at any time
future_result.status

# Get the output (blocking)
output = future_output.get()

# Inspect the output
output.input_data # Input data used by the QC program
output.success # Whether the calculation succeeded
output.results # All structured results from the calculation
output.stdout # Stdout log from the calculation
output.pstdout # Shortcut to print out the stdout in human readable format
output.files # Any files returned by the calculation
output.provenance # Provenance information about the calculation
output.extras # Any extra information not in the schema
output.traceback # Stack trace if calculation failed
output.ptraceback # Shortcut to print out the traceback in human readable format
```

## Examples

Examples of various computations can be found in the [/examples directory](https://github.com/mtzgroup/chemcloud-client/tree/main/examples).

## Usage

### Authentication

Authentication is the process of supplying your credentials (usually a username and password) to `chemcloud` so that you can perform computations. `chemcloud` provides a few easy ways for you to authenticate. If you do not have a ChemCloud account you can get one for free here or at the address of the ChemCloud server you want to interact with: [https://chemcloud.mtzlab.com/signup](https://chemcloud.mtzlab.com/signup)

#### `client.configure()` (recommended for most cases)

```python
from chemcloud import CCClient
client = CCClient()
client.configure()
✅ If you dont get have an account please signup at: https://chemcloud.mtzlab.com/signup
Please enter your ChemCloud username: your_username@email.com
Please enter your ChemCloud password:
Authenticating...
'default' profile configured! Username/password not required for future use of CCClient
```

Performing this action will configure your local client by writing authentication tokens to `~/.chemcloud/credentials`. You will not need to execute `configure()` ever again. Under the hood `CCClient` will access your tokens, refresh them when necessary, and keep you logged in to ChemCloud. Note that this will write a file to your home directory with sensitive access tokens, so if you are on a shared computer or using a device where you would not want to write this information to disk do not use this option. If you would like to write the `credentials` file to a different directory than `~/.chemcloud`, set the `CHEMCLOUD_BASE_DIRECTORY` environment variable to the path of interest.

You can configure multiple profiles in case you have multiple logins to ChemCloud by passing a profile name to `configure()`:

```python
client.configure('mtz_lab')
✅ If you dont get have an account please signup at: https://chemcloud.mtzlab.com/signup
Please enter your ChemCloud username: your_username@email.om
Please enter your ChemCloud password:
Authenticating...
'mtz_lab' profile configured! Username/password not required for future use of CCClient
```

To use one of these profiles pass the profile option to your client instance. The "default" profile is used when no profile name is passed:

```python
from chemcloud import CCClient
# Use default profile
client = CCClient()

# Use named profile
client = CCClient(profile="mtz_lab")
```

#### Environment Variables

You can set your ChemCloud username and password in your environment and the `client` will find them automatically. Set `CHEMCLOUD_USERNAME` and `CHEMCLOUD_PASSWORD`. When you create a client it will find these values and maintain all access tokens in memory only.

#### Username/Password when prompted after calling `client.compute(...)`

If you have not run `client.configure()` or set environment variables you will be requested for your username and password when you submit a computation to ChemCloud using `client.compute(...)`. The client will use your username and password to get access tokens and will maintain access tokens for you in memory only. Your login session will be valid for the duration of your python session.

#### Pass Username/Password to Client (not recommended)

You can directly pass a username and password to the `client` object. This is **not** recommended as it opens up the possibility of your credentials accidentally being committed to your code repo. However, it can be used in rare circumstances when necessary.

```python
from chemcloud import CCClient
client = CCClient(
    CHEMCLOUD_username="your_username@email.com", CHEMCLOUD_password="super_secret_password"  # pragma: allowlist secret
    )
```

### Batch Computations

Calculations can be submitted in bulk by passing a list of `Input` objects to `client.compute()` rather than a single object.

```python
client.compute("psi4", [input1, input2, input3])
```

### BigChem Algorithms

BigChem implements some of its own concurrent algorithms that leverage its horizontally scalable backend infrastructure. These include a parallel hessian algorithm and parallel frequency analysis algorithm. To use them submit a `hessian` calculation to ChemCloud using `bigchem` as the engine. See examples the `parallel_hessian.py` and `parallel_frequency_analysis.py` scripts in the [/examples](https://github.com/mtzgroup/chemcloud-client/tree/main/examples) directory.

Keywords for the BigChem algorithms:

| Keyword       | Type    | Description                                                | Default Value |
| :------------ | :------ | :--------------------------------------------------------- | :------------ |
| `dh`          | `float` | Displacement for gradient geometries for finite difference | `5.0e-3`      |
| `temperature` | `float` | Temperature passed to the harmonic free energy module      | `300.0`       |
| `pressure`    | `float` | Pressure passed to the harmonic free energy module         | `1.0`         |

## Support

If you have any issues with `chemcloud` or would like to request a feature, please open an [issue](https://github.com/mtzgroup/chemcloud-client/issues).
