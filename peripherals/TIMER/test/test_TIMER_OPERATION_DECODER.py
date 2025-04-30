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
    address = lib.Entity.Input_pin   # std_logic_vector(3 downto 0)
    write   = lib.Entity.Input_pin   # std_logic
    read    = lib.Entity.Input_pin   # std_logic

    # Outputs
    wr_en   = lib.Entity.Output_pin  # std_logic_vector(8 downto 0)
    cnt_sel = lib.Entity.Output_pin  # std_logic
    rd_sel  = lib.Entity.Output_pin  # std_logic_vector(2 downto 0)

# -----------------------------------------------------------------------------
# Address map -- must match exactly the VHDL decoder constants
# -----------------------------------------------------------------------------
ADDR = {
    # WRITE addresses
    "wr_start_stop": "0000",
    "wr_mode":       "0001",
    "wr_pwm_en":     "0010",
    "wr_load_timer": "0011",
    "wr_load_top":   "0100",
    "wr_load_duty":  "0101",
    "wr_irq_mask":   "0110",
    "wr_reset":      "0111",

    # READ addresses
    "rd_timer":      "1000",
    "rd_top":        "1001",
    "rd_duty":       "1010",
    "rd_configs":    "1011",
    "rd_pwm":        "1100",
    "rd_ovf_status": "1101",

    # Anything else → NOP / RESERVED
    "nop":           "1111",
}

# -----------------------------------------------------------------------------
# Drive address + strobes for one clock cycle
#   - dut: the DUT instance (TIMER_OPERATION_DECODER)
#   - trace: the waveform trace object (lib.Waveform)
#   - op: operation name (string) to be used for the address
# -----------------------------------------------------------------------------
async def dec_op(dut, trace, op: str, *, is_write: bool, is_read: bool):
    """Drives address + strobes for one clock cycle."""
    dut.address.value = BinaryValue(ADDR[op], n_bits=4)
    dut.write.value   = BinaryValue('1' if is_write else '0')
    dut.read.value    = BinaryValue('1' if is_read else '0')
    await trace.cycle()            # apply for exactly one cycle
    dut.write.value   = BinaryValue('0')
    dut.read.value    = BinaryValue('0')

# -----------------------------------------------------------------------------
# Expected results for WRITE-accesses
#   tuple: (operation-name, wr_en_bit_index, expected_cnt_sel)
# -----------------------------------------------------------------------------
WRITE_CASES = [
    ("wr_start_stop", 0, 0),
    ("wr_mode",       1, 0),
    ("wr_pwm_en",     2, 0),
    ("wr_load_timer", 3, 1),  # cnt_sel must pulse high on this write
    ("wr_load_top",   4, 0),
    ("wr_load_duty",  5, 0),
    ("wr_irq_mask",   6, 0),
    ("wr_reset",      8, 0),
]

# -----------------------------------------------------------------------------
# Expected results for READ-accesses
#   tuple: (operation-name, expected_rd_sel)
# -----------------------------------------------------------------------------
READ_CASES = [
    ("rd_timer",      "000"),
    ("rd_top",        "001"),
    ("rd_duty",       "010"),
    ("rd_configs",    "011"),
    ("rd_pwm",        "100"),
    ("rd_ovf_status", "101"),  # should also pulse wr_en(7)
    ("nop",           "111"),
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
        # Apply the WRITE operation
        await dec_op(dut, trace, name, is_write=True, is_read=False)

        exp_wr_en = format(1 << bit_i, "09b")
        # wr_en must match the address map
        yield trace.check(dut.wr_en, exp_wr_en, f"wr_en mismatch for WRITE op: {name}")
        # cnt_sel must pulse high on wr_load_timer (bit-3)
        yield trace.check(dut.cnt_sel, str(exp_cnt), f"cnt_sel mismatch for WRITE op: {name}")

    # ------------------------
    # READ decoding
    # ------------------------
    for name, exp_rd_sel in READ_CASES:
        # Apply the READ operation
        await dec_op(dut, trace, name, is_write=False, is_read=True)

        # rd_sel must match the address map
        yield trace.check(dut.rd_sel, exp_rd_sel, f"rd_sel mismatch for READ op: {name}")

        # wr_en pulses only on rd_ovf_status (bit-7)
        if name == "rd_ovf_status":
            yield trace.check(dut.wr_en, "010000000","wr_en(7) should pulse during rd_ovf_status")
        else:
            yield trace.check(dut.wr_en, "000000000",f"wr_en should be 0 during READ op: {name}")

        # cnt_sel must stay low on all pure READs
        yield trace.check(dut.cnt_sel, "0", f"cnt_sel should be 0 during READ op: {name}")

# -----------------------------------------------------------------------------
# Synthesis (lint / elaboration) smoke-check
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_TIMER_OPERATION_DECODER_synthesis():
    TIMER_OPERATION_DECODER.build_vhd()
    TIMER_OPERATION_DECODER.build_netlistsvg()

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
