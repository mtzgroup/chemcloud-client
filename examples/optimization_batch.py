from qcio import DualProgramInput, Structure

from chemcloud import CCClient

water = Structure(
    symbols=["O", "H", "H"],
    geometry=[
        [0.0000, 0.00000, 0.0000],
        [0.2774, 0.89290, 0.2544],
        [0.6067, -0.23830, -0.7169],
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
prog_output = future_result.get()

# Array of OptimizationOutput objects
print(prog_output)
