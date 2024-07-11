from qcio import DualProgramInput, OptimizationOutput, Structure

from chemcloud import CCClient

water = Structure(
    symbols=["O", "H", "H"],
    geometry=[
        [-0.11904094, -0.36695321, -0.21996706],
        [1.24615604, -0.14134141, 0.99915579],
        [-0.24300973, 1.16287522, -1.24168873],
    ],
)

client = CCClient()

prog_inp = DualProgramInput(
    structure=water,
    calctype="optimization",
    keywords={"maxiter": 25},
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
    # The final structure of the geometry optimization
    print(output.results.final_structure)
    # Initial structure
    print(output.input_data.structure)
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
