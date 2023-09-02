from pathlib import Path

from qcio import DualProgramInput, Molecule, SinglePointOutput

from chemcloud import CCClient

current_dir = Path(__file__).resolve().parent
water = Molecule.open(current_dir / "h2o.xyz")

client = CCClient()

prog_inp = DualProgramInput(
    molecule=water,
    calctype="hessian",
    subprogram="psi4",
    subprogram_args={"model": {"method": "b3lyp", "basis": "6-31g"}},
)


# Submit calculation
future_result = client.compute("bigchem", prog_inp)
output: SinglePointOutput = future_result.get()

# SinglePointOutput object containing all returned data
print(output)
print(output.results.hessian)
# Frequency data always included too
print(f"Wavenumbers: {output.results.freqs_wavenumber}")
print(output.results.normal_modes_cartesian)
print(output.results.gibbs_free_energy)
