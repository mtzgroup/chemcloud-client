from pathlib import Path

from qcio import Molecule, ProgramInput

from chemcloud import CCClient

current_dir = Path(__file__).resolve().parent
water = Molecule.open(current_dir / "h2o.xyz")

client = CCClient()

prog_inp = ProgramInput(
    molecule=water,
    model={"method": "b3lyp", "basis": "6-31g"},
    calctype="energy",
    keywords={},
)
future_result = client.compute("psi4", [prog_inp] * 2)
output = future_result.get()
# Array of SinglePointOutput objects containing all returned data
print(output)
