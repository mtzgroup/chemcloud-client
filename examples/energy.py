from tccloud import TCClient
from tccloud.models import AtomicInput, Molecule

client = TCClient()

water = Molecule.from_data("pubchem:water")
atomic_input = AtomicInput(
    molecule=water,
    model={"method": "B3LYP", "basis": "6-31g"},
    driver="energy",
    keywords={
        "closed": True,
        "restricted": True,
    },
    protocols={"stdout": True, "native_files": "all"},
    extras={"tcfe:keywords": {"native_files": ["c0"]}},
)
future_result = client.compute(atomic_input, engine="terachem_fe")
result = future_result.get()
# AtomicResult object containing all returned data
print(result)
# The energy value requested
print(result.return_result)
print(result.stdout)
print(result.native_files.keys())
