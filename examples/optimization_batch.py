from qcio import DualProgramInput, Structure

from chemcloud import compute

water = Structure(
    symbols=["O", "H", "H"],
    geometry=[
        [0.0000, 0.00000, 0.0000],
        [0.2774, 0.89290, 0.2544],
        [0.6067, -0.23830, -0.7169],
    ],
)


prog_inp = DualProgramInput(
    calctype="optimization",
    structure=water,
    keywords={"maxiter": 25},
    subprogram="psi4",
    subprogram_args={"model": {"method": "b3lyp", "basis": "6-31g"}},
)


# Submit calculation
output = compute("geometric", [prog_inp] * 2)
print(output)
