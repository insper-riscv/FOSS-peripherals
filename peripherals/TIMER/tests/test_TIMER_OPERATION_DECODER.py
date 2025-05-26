# test_TIMER_OPERATION_DECODER.py
# ============================================================================
# Functional test-bench for the VHDL entity: TIMER_OPERATION_DECODER
# ============================================================================

import pytest
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# -----------------------------------------------------------------------------
# Toplevel - VHDL wrapper
# -----------------------------------------------------------------------------
class TIMER_OPERATION_DECODER(lib.Entity):
    """Connects the TIMER_OPERATION_DECODER VHDL entity to the Python test-bench."""
    _package = GENERICS

    # Inputs
    address = lib.Entity.Input_pin   # std_logic_vector(2 downto 0)
    write   = lib.Entity.Input_pin   # std_logic
    read    = lib.Entity.Input_pin   # std_logic

    # Outputs
    wr_en   = lib.Entity.Output_pin  # std_logic_vector(5 downto 0)
    cnt_sel = lib.Entity.Output_pin  # std_logic
    rd_sel  = lib.Entity.Output_pin  # std_logic_vector(2 downto 0)

# -----------------------------------------------------------------------------
# Address map -- must match exactly the VHDL decoder constants
# -----------------------------------------------------------------------------
ADDR = {
    # WRITE addresses
    "wr_config":      "000",
    "wr_load_timer":  "001",
    "wr_reset":       "010",
    "wr_load_top":    "011",
    "wr_load_duty":   "100",
    "wr_prescaler":   "111",

    # READ addresses
    "rd_ovf_status":  "101",
    "rd_pwm":         "110",
    "rd_timer":       "001",
    "rd_top":         "011",
    "rd_duty":        "100",
    "rd_config":      "000",
    "rd_prescaler":    "111",
}

# -----------------------------------------------------------------------------
# Drive address + strobes for one clock cycle
# -----------------------------------------------------------------------------
async def dec_op(dut, trace, op: str, *, is_write: bool, is_read: bool):
    """Drives address + strobes for one clock cycle."""
    dut.address.value = BinaryValue(ADDR[op], n_bits=3)
    dut.write.value   = BinaryValue('1' if is_write else '0')
    dut.read.value    = BinaryValue('1' if is_read else '0')
    await trace.cycle()
    dut.write.value   = BinaryValue('0')
    dut.read.value    = BinaryValue('0')

# -----------------------------------------------------------------------------
# Expected results for WRITE-accesses
# -----------------------------------------------------------------------------
WRITE_CASES = [
    ("wr_config",      0, 0),
    ("wr_load_timer",  1, 1),
    ("wr_reset",       2, 0),
    ("wr_load_top",    3, 0),
    ("wr_load_duty",   4, 0),
    ("wr_prescaler", 6, 0),
]

# -----------------------------------------------------------------------------
# Expected results for READ-accesses
# -----------------------------------------------------------------------------
READ_CASES = [
    ("rd_timer",       "000"),
    ("rd_top",         "001"),
    ("rd_duty",        "010"),
    ("rd_config",      "011"),
    ("rd_pwm",         "100"),
    ("rd_ovf_status",  "101"),
    ("rd_prescaler",    "110"),
]

# -----------------------------------------------------------------------------
# Functional verification
# -----------------------------------------------------------------------------
@TIMER_OPERATION_DECODER.testcase
async def tb_timer_operation_decoder_manual(dut: TIMER_OPERATION_DECODER, trace: lib.Waveform):
    """Verifies write-decoding, read-decoding, and cnt_sel behaviour."""

    # ------------------------
    # WRITE decoding
    # ------------------------
    for name, bit_i, exp_cnt in WRITE_CASES:
        await dec_op(dut, trace, name, is_write=True, is_read=False)

        exp_wr_en = format(1 << bit_i, "07b")
        print(f"Expected wr_en for {name}: {exp_wr_en}")
        yield trace.check(dut.wr_en, exp_wr_en, f"wr_en mismatch for WRITE op: {name}")
        yield trace.check(dut.cnt_sel, str(exp_cnt), f"cnt_sel mismatch for WRITE op: {name}")

    # ------------------------
    # READ decoding
    # ------------------------
    for name, exp_rd_sel in READ_CASES:
        await dec_op(dut, trace, name, is_write=False, is_read=True)

        yield trace.check(dut.rd_sel, exp_rd_sel, f"rd_sel mismatch for READ op: {name}")

        if name == "rd_ovf_status":
            yield trace.check(dut.wr_en, "0100000", "wr_en(5) should pulse during rd_ovf_status")
        else:
            yield trace.check(dut.wr_en, "0000000", f"wr_en should be 0 during READ op: {name}")

        yield trace.check(dut.cnt_sel, "0", f"cnt_sel should be 0 during READ op: {name}")

# -----------------------------------------------------------------------------
# Synthesis (lint / elaboration) smoke-check
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_TIMER_OPERATION_DECODER_synthesis():
    TIMER_OPERATION_DECODER.build_vhd()


# -----------------------------------------------------------------------------
# Test-run wrapper for pytest
# -----------------------------------------------------------------------------
@pytest.mark.testcases
def test_timer_operation_decoder_manual():
    TIMER_OPERATION_DECODER.test_with(tb_timer_operation_decoder_manual)

# -----------------------------------------------------------------------------
# Stand-alone entry-point (optional)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    lib.run_test(__file__)
