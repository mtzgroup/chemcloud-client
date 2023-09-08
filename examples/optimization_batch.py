from pathlib import Path

from qcio import DualProgramInput, Molecule

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
future_result = client.compute("geometric", [prog_inp] * 2)
output = future_result.get()

# Array of OptimizationOutput objects
print(output)
