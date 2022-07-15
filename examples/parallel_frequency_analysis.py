from qccloud import QCClient
from qccloud.models import AtomicInput, Molecule

client = QCClient()

water = Molecule.from_data("pubchem:water")

# Frequency Analysis
atomic_input = AtomicInput(
    molecule=water,
    model={"method": "B3LYP", "basis": "6-31g"},
    driver="properties",
    extras={
        "bigqc:keywords": {
            "temperature": 380.0,  # OPTIONAL: temperature for free energy calculation
        },
    },
)
future_result = client.compute(atomic_input, engine="bigqc")
result = future_result.get()
# AtomicResult object containing all returned data
print(result)
# Dictionary containing frequency analysis results
print(result.return_result)
