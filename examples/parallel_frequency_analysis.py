from qcio import DualProgramInput, Molecule, SinglePointOutput

from chemcloud import CCClient

water = Molecule(
    symbols=["O", "H", "H"],
    geometry=[
        [0.0000, 0.00000, 0.0000],
        [0.2774, 0.89290, 0.2544],
        [0.6067, -0.23830, -0.7169],
    ],
)

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
print(f"Wavenumbers: {output.results.freqs_wavenumber}")
print(output.results.normal_modes_cartesian)
print(output.results.gibbs_free_energy)
