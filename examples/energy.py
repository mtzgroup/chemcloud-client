from qcio import ProgramInput, Structure

from chemcloud import compute

water = Structure(
    symbols=["O", "H", "H"],
    geometry=[
        [0.0000, 0.00000, 0.0000],
        [0.2774, 0.89290, 0.2544],
        [0.6067, -0.23830, -0.7169],
    ],
)


prog_inp = ProgramInput(
    calctype="energy",  # Or "gradient" or "hessian"
    structure=water,
    model={"method": "b3lyp", "basis": "6-31g"},
    keywords={},
)
output = compute("terachem", prog_inp)
# ProgramOutput object containing all returned data
print(output.stdout)
print(output)

if output.success:
    print(output.results.energy)
    # Not empty if collect_files=True passed to compute
    print(output.results.files.keys())
else:
    print(output.traceback)
