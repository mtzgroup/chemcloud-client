import asyncio

from qcio import CalcType, ProgramInput, Structure

from chemcloud import compute_async

water = Structure(
    symbols=["O", "H", "H"],
    geometry=[
        [0.0000, 0.00000, 0.0000],
        [0.2774, 0.89290, 0.2544],
        [0.6067, -0.23830, -0.7169],
    ],
    connectivity=[[0, 1, 1.0], [0, 2, 1.0]],
)

prog_inp = ProgramInput(
    calctype=CalcType.energy,
    structure=water,
    model={"method": "UFF"},
)

output = asyncio.run(compute_async("rdkit", prog_inp))
print(output)
