from pathlib import Path

from qcio import Molecule, ProgramInput, SinglePointOutput

from chemcloud import CCClient

current_dir = Path(__file__).resolve().parent
water = Molecule.open(current_dir / "h2o.xyz")

client = CCClient()

prog_inp = ProgramInput(
    molecule=water,
    model={"method": "b3lyp", "basis": "6-31gg"},
    calctype="energy",
    keywords={},
)
future_result = client.compute("psi4", prog_inp, collect_files=True)
output: SinglePointOutput = future_result.get()
# SinglePointOutput object containing all returned data
print(output.stdout)
print(output)
# The energy value requested
print(output.return_result)
print(output.files.keys())
