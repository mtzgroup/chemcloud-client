from base64 import b64decode, b64encode
from typing import Any, Dict, List, Union

from .config import settings
from .models import AtomicInputOrList, OptimizationInput, OptimizationInputOrList

B64_POSTFIX = "_b64"


def _bytes_to_b64(
    input_data: Union[AtomicInputOrList, OptimizationInputOrList]
) -> None:
    """Convert binary input data to base64 encoded strings"""

    if not isinstance(input_data, list):
        input_data = [input_data]

    if isinstance(input_data[0], OptimizationInput):
        input_data = [opt.input_specification for opt in input_data]

    for inp in input_data:
        tcfe_config = inp.extras.get(settings.tcfe_keywords, {})
        binary_files = [
            key for key, value in tcfe_config.items() if isinstance(value, bytes)
        ]
        for key in binary_files:
            file_bytes = tcfe_config.pop(key)
            tcfe_config[f"{key}{B64_POSTFIX}"] = b64encode(file_bytes).decode()


def _b64_to_bytes_dict(inp: Dict[str, Any]):
    """Change b64 encoded dict values to binary"""
    b64_keys = [key for key in inp.keys() if key.endswith(B64_POSTFIX)]
    for key in b64_keys:
        value = inp.pop(key)
        inp[key.split(B64_POSTFIX)[0]] = b64decode(value)


def _b64_to_bytes(results: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
    """Convert b64 encoded native_files and input data to bytes. Modifies objects in place.

    Parameters:
        results: Dictionary representation of models.PossibleResultsOrList
    """
    if not isinstance(results, list):
        results = [results]

    for result in results:
        if result["success"]:
            # AtomicResult or OptimizationResult dictionary
            if result.get("final_molecule"):
                # Is OptimizationResult dict
                for ai in result["trajectory"]:
                    # Have to do .get() or {} due to native_files = Optional[Dict]
                    # See https://github.com/MolSSI/QCElemental/pull/285
                    _b64_to_bytes_dict(ai.get("native_files") or {})
                    _b64_to_bytes_dict(ai["extras"].get(settings.tcfe_keywords) or {})
            else:
                # Is AtomicInput dict
                _b64_to_bytes_dict(result.get("native_files") or {})
                _b64_to_bytes_dict(result["extras"].get(settings.tcfe_keywords) or {})
