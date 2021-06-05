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
future_result = client.compute_procedure([opt_input] * 2, "berny")
result = future_result.get()
# Array of OptimizationResult objects
print(result)
