from tccloud.models import (
    AtomicInput,
    AtomicResult,
    OptimizationInput,
    OptimizationResult,
)
from tccloud.utils import B64_POSTFIX, _b64_to_bytes, _bytes_to_b64


def test_bytes_to_b64(water, settings):
    ai = AtomicInput(
        molecule=water,
        model={"method": "b3lyp", "basis": "6-31g"},
        driver="energy",
        extras={settings.tcfe_keywords: {"c0": b"123"}},
    )
    _bytes_to_b64(ai)

    assert ai.extras[settings.tcfe_keywords].get("c0") is None
    assert ai.extras[settings.tcfe_keywords].get(f"c0{B64_POSTFIX}") == "MTIz"


def test_bytes_to_b64_opt_inp(water, settings):
    opt = OptimizationInput(
        initial_molecule=water,
        input_specification={
            "model": {"method": "b3lyp", "basis": "6-31g"},
            "driver": "energy",
            "extras": {settings.tcfe_keywords: {"c0": b"123"}},
        },
    )
    _bytes_to_b64(opt)

    assert opt.input_specification.extras[settings.tcfe_keywords].get("c0") is None
    assert (
        opt.input_specification.extras[settings.tcfe_keywords].get(f"c0{B64_POSTFIX}")
        == "MTIz"
    )


def test_bytes_to_b64_list(water, settings):
    ai = AtomicInput(
        molecule=water,
        model={"method": "b3lyp", "basis": "6-31g"},
        driver="energy",
        extras={settings.tcfe_keywords: {"c0": b"123"}},
    )
    input_data = [ai, AtomicInput(**ai.dict())]
    _bytes_to_b64(input_data)

    for ai in input_data:
        assert ai.extras[settings.tcfe_keywords].get("c0") is None
        assert ai.extras[settings.tcfe_keywords].get(f"c0{B64_POSTFIX}") == "MTIz"


def test_bytes_to_b64_opt_inp_list(water, settings):
    opt = OptimizationInput(
        initial_molecule=water,
        input_specification={
            "model": {"method": "b3lyp", "basis": "6-31g"},
            "driver": "energy",
            "extras": {settings.tcfe_keywords: {"c0": b"123"}},
        },
    )
    [opt, OptimizationInput(**opt.dict())]
    _bytes_to_b64(opt)

    assert opt.input_specification.extras[settings.tcfe_keywords].get("c0") is None
    assert (
        opt.input_specification.extras[settings.tcfe_keywords].get(f"c0{B64_POSTFIX}")
        == "MTIz"
    )


def test_b64_to_bytes_atomic_result(water, settings):
    ar_dict = AtomicResult(
        molecule=water,
        model={"method": "b3lyp", "basis": "6-31g"},
        driver="energy",
        extras={settings.tcfe_keywords: {f"c0{B64_POSTFIX}": "MTIz"}},
        return_result=123.4,
        provenance={"creator": "test suite"},
        properties={},
        success=True,
        protocols={"native_files": "all"},
        native_files={f"c0{B64_POSTFIX}": "MTIz"},
    ).dict()
    _b64_to_bytes(ar_dict)

    assert ar_dict["extras"][settings.tcfe_keywords].get(f"c0{B64_POSTFIX}") is None
    assert ar_dict["extras"][settings.tcfe_keywords].get("c0") == b"123"

    assert ar_dict["native_files"].get(f"c0{B64_POSTFIX}") is None
    assert ar_dict["native_files"].get("c0") == b"123"


def test_b64_to_bytes_opt_result(water, settings):
    or_dict = OptimizationResult(
        initial_molecule=water,
        final_molecule=water,
        success=True,
        provenance={"creator": "test suite"},
        energies=[123.4, 567.8],
        input_specification={
            "model": {"method": "b3lyp", "basis": "6-31g"},
            "driver": "energy",
            "extras": {settings.tcfe_keywords: {"c0": b"123"}},
        },
        trajectory=[
            AtomicResult(
                molecule=water,
                model={"method": "b3lyp", "basis": "6-31g"},
                driver="energy",
                extras={settings.tcfe_keywords: {"c0": b"123"}},
                return_result=123.4,
                provenance={"creator": "test suite"},
                properties={},
                success=True,
                protocols={"native_files": "all"},
                native_files={"c0_b64": "MTIz"},
            ),
            AtomicResult(
                molecule=water,
                model={"method": "b3lyp", "basis": "6-31g"},
                driver="energy",
                extras={settings.tcfe_keywords: {"c0": b"123"}},
                return_result=123.4,
                provenance={"creator": "test suite"},
                properties={},
                success=True,
                protocols={"native_files": "all"},
                native_files={"c0_b64": "MTIz"},
            ),
        ],
    ).dict()
    _b64_to_bytes(or_dict)

    for ar in or_dict["trajectory"]:
        assert ar["native_files"].get(f"c0{B64_POSTFIX}") is None
        assert ar["native_files"].get("c0") == b"123"
