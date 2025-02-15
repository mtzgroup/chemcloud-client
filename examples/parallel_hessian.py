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
    structure=water,
    calctype="hessian",
    subprogram="psi4",
    subprogram_args={"model": {"method": "b3lyp", "basis": "6-31g"}},
)


# Submit calculation
output = compute("bigchem", prog_inp)

# ProgramOutput object containing all returned data
print(output)
print(output.results.hessian)
# Frequency data always included too
print(f"Wavenumbers: {output.results.freqs_wavenumber}")
print(output.results.normal_modes_cartesian)
print(output.results.gibbs_free_energy)
