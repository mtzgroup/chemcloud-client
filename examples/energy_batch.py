from qcio import ProgramInput, Structure

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

prog_inp = ProgramInput(
    structure=water,
    model={"method": "b3lyp", "basis": "6-31g"},
    calctype="energy",
    keywords={},
)
future_result = client.compute("psi4", [prog_inp] * 2)
prog_output = future_result.get()
# Array of ProgramOutput objects containing all returned data
print(prog_output)
