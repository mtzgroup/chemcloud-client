from qcio import Molecule, ProgramInput, ProgramOutput

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

prog_inp = ProgramInput(
    molecule=water,
    model={"method": "b3lyp", "basis": "6-31g"},
    calctype="energy",  # Or "gradient" or "hessian"
    keywords={},
)
future_result = client.compute("terachem", prog_inp, collect_files=True)
prog_output: ProgramOutput = future_result.get()
# ProgramOutput object containing all returned data
print(prog_output.stdout)
print(prog_output)
# The energy value requested

if prog_output.success:
    print(prog_output.results.energy)
    print(prog_output.files.keys())
else:
    print(prog_output.traceback)
