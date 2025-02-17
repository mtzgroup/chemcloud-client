import logging
from time import time

from qcio import ProgramInput, Structure

from chemcloud import compute

# Configure the root logger (for all logs)
logging.basicConfig(
    level=logging.WARNING,  # Default: only show warnings and errors globally
    format="[%(levelname)s] %(name)s: %(message)s",
)

# Configure only the chemcloud logger for DEBUG logs
chemcloud_logger = logging.getLogger("chemcloud")
chemcloud_logger.setLevel(logging.DEBUG)  # Enable detailed logs for chemcloud


water = Structure(
    symbols=["O", "H", "H"],
    geometry=[
        [0.0000, 0.00000, 0.0000],
        [0.2774, 0.89290, 0.2544],
        [0.6067, -0.23830, -0.7169],
    ],
    connectivity=[(0, 1, 1.0), (0, 2, 1.0)],
)

# client = CCClient()

prog_inp = ProgramInput(
    structure=water,
    # model={"method": "b3lyp", "basis": "6-31g"},
    model={"method": "UFF"},
    calctype="energy",  # Or "gradient" or "hessian"
    keywords={},
)

prog_inputs = [prog_inp] * 100
start = time()
frs = compute("rdkit", prog_inputs, collect_stdout=False, return_future=True)
end = time()

print(f"Inputs submitted in: {end - start:.2f} seconds")

start = time()
outputs = frs.get()
end = time()
print(f"Outputs collected in {end - start:.2f} seconds")
print(f"All success: {all([o.success for o in outputs])}")
