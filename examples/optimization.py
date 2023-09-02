from pathlib import Path

from qcio import DualProgramInput, Molecule, OptimizationOutput

from chemcloud import CCClient

current_dir = Path(__file__).resolve().parent
water = Molecule.open(current_dir / "h2o.xyz")

client = CCClient()

prog_inp = DualProgramInput(
    molecule=water,
    calctype="optimization",
    keywords={"maxiter": 3},
    subprogram="psi4",
    subprogram_args={"model": {"method": "b3lyp", "basis": "6-31g"}},
)


# Submit calculation
future_result = client.compute("geometric", prog_inp)
output: OptimizationOutput = future_result.get()

if output.success:
    print("Optimization succeeded!")
    # Will be OptimizationResult object
    print(output)
    # The final molecule of the geometry optimization
    print(output.results.final_molecule)
    # Initial molecule
    print(output.input_data.molecule)
    # A list of ordered AtomicResult objects for each step in the optimization
    print(output.results.trajectory)
    # A list of ordered energies for each step in the optimization
    print(output.results.energies)
else:
    print("Optimization failed!")
    # Will be FailedOperation object
    print(output)
    # Error information
    print(output.traceback)
