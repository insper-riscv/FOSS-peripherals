# test_CLOCK_PRESCALER.py
# =============================================================================
# Functional test-bench for the VHDL entity: CLOCK_PRESCALER
# =============================================================================

import pytest
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# -----------------------------------------------------------------------------
# Python-to-VHDL wrapper
# -----------------------------------------------------------------------------
class CLOCK_PRESCALER(lib.Entity):
    _package = GENERICS

    clock        = lib.Entity.Input_pin
    clear        = lib.Entity.Input_pin
    prescaler_in = lib.Entity.Input_pin
    tick         = lib.Entity.Output_pin

# -----------------------------------------------------------------------------
# Binary vector helper
# -----------------------------------------------------------------------------
def bv(val: int, width: int = 32):
    return BinaryValue(value=val, n_bits=width, bigEndian=False)

# -----------------------------------------------------------------------------
# Test Case: Prescaler Tick at Defined Value
# -----------------------------------------------------------------------------
@CLOCK_PRESCALER.testcase
async def tb_prescaler_basic(dut: CLOCK_PRESCALER, trace: lib.Waveform):
    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")

    # Set prescaler value to 4
    dut.prescaler_in.value = bv(4)

    # Should tick after 5 cycles (0..4)
    for i in range(5):
        await trace.cycle()
        if i < 4:
            yield trace.check(dut.tick, BinaryValue("0"), f"Tick should be 0 at cycle {i}")
        else:
            yield trace.check(dut.tick, BinaryValue("1"), f"Tick should be 1 at cycle {i}")

    # Next cycle should reset counter → tick = 0
    await trace.cycle()
    yield trace.check(dut.tick, BinaryValue("0"), "Tick should reset after pulse")

# -----------------------------------------------------------------------------
# Test Case: Clear Resets Counter
# -----------------------------------------------------------------------------
@CLOCK_PRESCALER.testcase
async def tb_prescaler_clear(dut: CLOCK_PRESCALER, trace: lib.Waveform):
    # Apply clear
    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")
    await trace.cycle()  # ← este ciclo extra é essencial

    dut.prescaler_in.value = bv(3)

    # Let it count 2 cycles
    for i in range(2):
        await trace.cycle()
        yield trace.check(dut.tick, BinaryValue("0"), f"Tick should be 0 at cycle {i}")

    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")
    # Counter should restart → tick only after 4 cycles from here
    for i in range(4):
        await trace.cycle()
        expected = "1" if i == 3 else "0"
        yield trace.check(dut.tick, BinaryValue(expected), f"Tick after clear at cycle {i}")

# -----------------------------------------------------------------------------
# Synthesis smoke-check
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_CLOCK_PRESCALER_synthesis():
    CLOCK_PRESCALER.build_vhd()

# -----------------------------------------------------------------------------
# Pytest test entry point
# -----------------------------------------------------------------------------
@pytest.mark.testcases
def test_prescaler_basic():
    CLOCK_PRESCALER.test_with(tb_prescaler_basic)

@pytest.mark.testcases
def test_prescaler_clear():
    CLOCK_PRESCALER.test_with(tb_prescaler_clear)

if __name__ == "__main__":
    lib.run_test(__file__)
