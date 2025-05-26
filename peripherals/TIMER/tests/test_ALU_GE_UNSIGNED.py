# test_ALU_GE_UNSIGNED.py
# ============================================================================
# Functional test-bench for the VHDL entity: ALU_GE_UNSIGNED
# Implements a pure combinational greater-equal comparator (unsigned)
# Uses the same test-framework conventions adopted for decoder modules
# ============================================================================

import pytest
import random
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# -----------------------------------------------------------------------------
# Toplevel - VHDL wrapper
# -----------------------------------------------------------------------------
class ALU_GE_UNSIGNED(lib.Entity):
    """Connects the ALU_GE_UNSIGNED VHDL entity to the Python test-bench."""
    _package = GENERICS

    # Inputs
    source_1 = lib.Entity.Input_pin   # std_logic_vector(DATA_WIDTH-1 downto 0)
    source_2 = lib.Entity.Input_pin   # std_logic_vector(DATA_WIDTH-1 downto 0)

    # Output
    ge       = lib.Entity.Output_pin  # std_logic ('1' if source_1 >= source_2)

# -----------------------------------------------------------------------------
# Drive source_1 and source_2 and wait one cycle
# -----------------------------------------------------------------------------
async def apply(dut, trace, a: int, b: int, width: int):
    """Drives A and B into the DUT and advances one cycle."""
    dut.source_1.value = BinaryValue(a, n_bits=width, bigEndian=False)
    dut.source_2.value = BinaryValue(b, n_bits=width, bigEndian=False)
    await trace.cycle()

# -----------------------------------------------------------------------------
# Functional verification
# -----------------------------------------------------------------------------
@ALU_GE_UNSIGNED.testcase
async def tb_ALU_GE_UNSIGNED(dut: ALU_GE_UNSIGNED, trace: lib.Waveform):
    """Verifies unsigned greater-equal logic against Python's >= operator."""

    width = int(getattr(dut, "DATA_WIDTH", 32))
    max_val = (1 << width) - 1

    # Static edge cases
    test_vectors = [
        (0, 0),
        (max_val, max_val),
        (0, max_val),
        (max_val, 0),
        (0, 1),
        (1, 0),
        (max_val - 1, max_val),
        (max_val, max_val - 1),
    ]

    for a, b in test_vectors:
        await apply(dut, trace, a, b, width)
        expected = '1' if a >= b else '0'
        yield trace.check(dut.ge, expected, f"ge mismatch for A={a:#0{width//4+2}x}, B={b:#0{width//4+2}x} (expected {expected})")

    # Per-bit edge cases
    for i in range(width):
        below = (1 << i) - 1
        exact = (1 << i)
        await apply(dut, trace, below, exact, width)
        yield trace.check(dut.ge, '0', f"ge failed: {below} >= {exact} expected 0")
        await apply(dut, trace, exact, below, width)
        yield trace.check(dut.ge, '1', f"ge failed: {exact} >= {below} expected 1")

    # Midpoint symmetry
    half = 1 << (width - 1)
    await apply(dut, trace, half - 1, half, width)
    yield trace.check(dut.ge, '0', f"ge failed: {half - 1} >= {half} expected 0")
    await apply(dut, trace, half, half - 1, width)
    yield trace.check(dut.ge, '1', f"ge failed: {half} >= {half - 1} expected 1")

# -----------------------------------------------------------------------------
# Synthesis (lint / elaboration) smoke-check
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_ALU_GE_UNSIGNED_synthesis():
    ALU_GE_UNSIGNED.build_vhd()

# -----------------------------------------------------------------------------
# Test-run wrapper for pytest
# -----------------------------------------------------------------------------
@pytest.mark.testcases
def test_ALU_GE_UNSIGNED():
    ALU_GE_UNSIGNED.test_with(tb_ALU_GE_UNSIGNED)

# -----------------------------------------------------------------------------
# Stand-alone entry-point (optional)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    lib.run_test(__file__)
