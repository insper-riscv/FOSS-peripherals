import pytest
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# -----------------------------------------------------------------------------
# Toplevel GPIO Operation Decoder Wrapper
# -----------------------------------------------------------------------------
class GPIO_OPERATION_DECODER(lib.Entity):
    """This class connects the GPIO_OPERATION_DECODER entity to the test framework.
    The ports declared here mirror the VHDL interface.
    """
    _package = GENERICS

    address = lib.Entity.Input_pin   # Input: Address bus (4 bits)
    write   = lib.Entity.Input_pin   # Input: Write signal

    wr_en   = lib.Entity.Output_pin  # Output: Write enable vector (7 bits)
    wr_op   = lib.Entity.Output_pin  # Output: Write operation selector (2 bits)
    rd_sel  = lib.Entity.Output_pin  # Output: Read selector for readback multiplexer (3 bits)

# -----------------------------------------------------------------------------
# Address map used for testing — mirrors the decoder's internal map
# -----------------------------------------------------------------------------
ADDR = {
    "wr_dir":        "0000",
    "wr_out_load":   "0001",
    "wr_out_set":    "0010",
    "wr_out_clear":  "0011",
    "wr_out_toggle": "0100",
    "wr_irq_mask":   "0101",
    "wr_rise_mask":  "0110",
    "wr_fall_mask":  "0111",
    "wr_irq_clr":    "1000",
    "rd_dir":        "1001",
    "rd_out":        "1010",
    "rd_pins":       "1011",
    "rd_irq_stat":   "1100",
    "rd_irq_mask":   "1101",
    "rd_rise_mask":  "1110",
    "rd_fall_mask":  "1111",
    "nop":           "0000",  # For read test fallback
}

# -----------------------------------------------------------------------------
# Stimulus helper: apply one transaction to the decoder
# -----------------------------------------------------------------------------
async def dec_op(dut, trace, op, write=False):
    """Drives address and write signals to evaluate decoder output.
    """
    dut.address.value = BinaryValue(ADDR[op], n_bits=4)
    dut.write.value = BinaryValue('1' if write else '0')
    await trace.cycle()
    dut.write.value = BinaryValue('0')

# -----------------------------------------------------------------------------
# Write decoding test cases (address, wr_en index, expected wr_op value)
# -----------------------------------------------------------------------------
WRITE_CASES = [
    ("wr_dir",        0, "00"),
    ("wr_out_load",   1, "00"),
    ("wr_out_set",    2, "01"),
    ("wr_out_clear",  2, "10"),
    ("wr_out_toggle", 2, "11"),
    ("wr_irq_mask",   3, "00"),
    ("wr_rise_mask",  4, "00"),
    ("wr_fall_mask",  5, "00"),
    ("wr_irq_clr",    6, "00"),
]

# Read decoding expectations (address, expected rd_sel value)
READ_CASES = [
    ("rd_dir",       "000"),
    ("rd_out",       "001"),
    ("rd_pins",      "010"),
    ("rd_irq_stat",  "011"),
    ("rd_irq_mask",  "100"),
    ("rd_rise_mask", "101"),
    ("rd_fall_mask", "110"),
    ("nop",          "111"),
]

# -----------------------------------------------------------------------------
# Functional Test: write and read decoding logic
# -----------------------------------------------------------------------------
@GPIO_OPERATION_DECODER.testcase
async def tb_operation_decoder_manual(dut: GPIO_OPERATION_DECODER, trace: lib.Waveform):
    """Verifies correct decoder output for all write and read address values.

    WRITE: Only one bit in wr_en active, correct wr_op code.
    READ: Correct rd_sel and wr_en = 0000000.
    """
    # Write decoding tests
    for name, bit_i, exp_wr_op in WRITE_CASES:
        await dec_op(dut, trace, name, write=True)
        exp_wr_en = format(1 << bit_i, '07b')
        yield trace.check(dut.wr_en, exp_wr_en, f"wr_en mismatch for {name}")
        yield trace.check(dut.wr_op, exp_wr_op, f"wr_op mismatch for {name}")

    # Read decoding tests
    for name, exp_rd_sel in READ_CASES:
        await dec_op(dut, trace, name, write=False)
        yield trace.check(dut.rd_sel, exp_rd_sel, f"rd_sel mismatch for {name}")
        yield trace.check(dut.wr_en, "0000000", f"wr_en should be 0 during read: {name}")

# -----------------------------------------------------------------------------
# Synthesis test: ensure the VHDL file builds in isolation
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_GPIO_OPERATION_DECODER_synthesis():
    GPIO_OPERATION_DECODER.build_vhd()

# -----------------------------------------------------------------------------
# Manual test execution hook
# -----------------------------------------------------------------------------
@pytest.mark.testcases
def test_gpio_operation_decoder_manual():
    GPIO_OPERATION_DECODER.test_with(tb_operation_decoder_manual)

# -----------------------------------------------------------------------------
# Direct execution entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    lib.run_test(__file__)
