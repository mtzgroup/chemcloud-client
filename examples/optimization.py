from pprint import pprint

from tccloud import TCClient
from tccloud.models import Molecule, OptimizationInput, QCInputSpecification

client = TCClient()

water = Molecule.from_data("pubchem:water")

input_spec = QCInputSpecification(
    model={"method": "b3lyp", "basis": "6-31g"},
    # Keywords for the compute engine (e.g., psi4, terachem_pbs)
    keywords={},
)

opt_input = OptimizationInput(
    initial_molecule=water,
    input_specification=input_spec,
    # Trajectory molecules to include in result, may be one of:
    # 'all' or 'initial_and_final' or 'final' or 'none'
    protocols={"trajectory": "all"},
    # Must define compute engine "program": "engine_name"
    # Define keywords for optimizer (pyberny or geomeTRIC)
    keywords={"program": "terachem_pbs", "maxsteps": 3},
)


# Optimizer can be "berny" or "geometric"
future_result = client.compute_procedure(opt_input, "berny")
result = future_result.get()

if result.success:
    print("Optimization succeeded!")
    # Will be OptimizationResult object
    print(result)
    # The final molecule of the geometry optimization
    print(result.final_molecule)
    # Initial molecule
    print(result.initial_molecule)
    # A list of ordered AtomicResult objects for each step in the optimization
    print(result.trajectory)
    # A list of ordered energies for each step in the optimization
    print(result.energies)
else:
    print("Optimization failed!")
    # Will be FailedOperation object
    print(result)
    # Error information
    print(result.error)
    # Detailed error message
    pprint(result.error.error_message)
