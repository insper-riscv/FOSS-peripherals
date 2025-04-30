# test_COUNTER_OVERFLOW.py
# ============================================================================
# Functional test-bench for the VHDL entity: COUNTER_OVERFLOW
# ----------------------------------------------------------------------------
# Description:
#   • Purely combinational unit — no clock
#   • Generates a pulse on overflow when:
#       – TOP is reached/exceeded: counter_value ≥ top_value
# ============================================================================

import pytest
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# -----------------------------------------------------------------------------
# Toplevel — VHDL wrapper
# -----------------------------------------------------------------------------
class COUNTER_OVERFLOW(lib.Entity):
    """Connects the COUNTER_OVERFLOW VHDL entity to the Python test framework."""
    _package = GENERICS

    # Input signals
    counter_value = lib.Entity.Input_pin
    top_value     = lib.Entity.Input_pin

    # Output signal
    overflow      = lib.Entity.Output_pin  # Combinational overflow pulse


# -----------------------------------------------------------------------------
# Apply stimulus and advance simulation by one cycle
# -----------------------------------------------------------------------------
async def apply(dut, trace, cnt: int, top: int, width: int):
    """Drives inputs (counter, top) for one waveform cycle."""
    dut.counter_value.value = BinaryValue(cnt, n_bits=width, bigEndian=False)
    dut.top_value.value     = BinaryValue(top, n_bits=width, bigEndian=False)
    await trace.cycle()


# -----------------------------------------------------------------------------
# Test vectors — (counter_value, top_value, expected_overflow)
# -----------------------------------------------------------------------------
def mk_vectors(width: int):
    """Generates test cases for top-reach detection logic."""
    max_val = (1 << width) - 1
    half    = 1 << (width - 1)

    return [
        # ----------------------------
        # NORMAL CONDITIONS — no overflow
        # ----------------------------
        (0,          max_val, 0),
        (half,       max_val, 0),
        (max_val-1,  max_val, 0),

        # ----------------------------
        # TOP REACHED OR BREACHED
        # ----------------------------
        (max_val,    max_val, 1),
        (max_val,    max_val-1, 1),
        (10,         8,        1),
        (8,          8,        1),
    ]


# -----------------------------------------------------------------------------
# Functional verification
# -----------------------------------------------------------------------------
@COUNTER_OVERFLOW.testcase
async def tb_counter_overflow(dut: COUNTER_OVERFLOW, trace: lib.Waveform):
    """Verifies overflow flag for top-reach detection."""

    width = int(getattr(dut, "DATA_WIDTH", 32))

    for cnt, top, exp in mk_vectors(width):
        # Apply the test vector
        await apply(dut, trace, cnt, top, width)

        msg = (f"overflow mismatch: "f"CNT={cnt:#0{width//4+2}x}, "
               f"TOP={top:#0{width//4+2}x} → expected={exp}")

        yield trace.check(dut.overflow, str(exp), msg)


# -----------------------------------------------------------------------------
# Synthesis / elaboration smoke-check
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_COUNTER_OVERFLOW_synthesis():
    COUNTER_OVERFLOW.build_vhd()
    COUNTER_OVERFLOW.build_netlistsvg()


# -----------------------------------------------------------------------------
# Test-run wrapper for pytest
# -----------------------------------------------------------------------------
@pytest.mark.testcases
def test_counter_overflow():
    COUNTER_OVERFLOW.test_with(tb_counter_overflow)


# -----------------------------------------------------------------------------
# Stand-alone entry-point (optional)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    lib.run_test(__file__)