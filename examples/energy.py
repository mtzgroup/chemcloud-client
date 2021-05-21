from tccloud import TCClient
from tccloud.models import AtomicInput, Molecule

client = TCClient()
water = Molecule.from_data("pubchem:water")
atomic_input = AtomicInput(
    molecule=water, model={"method": "B3LYP", "basis": "6-31g"}, driver="energy"
)
future_result = client.compute(atomic_input, engine="terachem_pbs")
result = future_result.get()
# AtomicResult object containing all returned data
print(result)
# The energy value requested
print(result.return_result)
