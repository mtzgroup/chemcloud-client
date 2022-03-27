from tccloud import TCClient
from tccloud.models import AtomicInput, Molecule

client = TCClient()

water = Molecule.from_data("pubchem:water")

# Frequency Analysis
atomic_input = AtomicInput(
    molecule=water,
    model={"method": "B3LYP", "basis": "6-31g"},
    driver="properties",
    extras={
        "tcc:keywords": {
            "temperature": 380.0,  # OPTIONAL: temperature for free energy calculation
        },
    },
)
future_result = client.compute(atomic_input, engine="tcc")
result = future_result.get()
# AtomicResult object containing all returned data
print(result)
# Dictionary containing frequency analysis results
print(result.return_result)
