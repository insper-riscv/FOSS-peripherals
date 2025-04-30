import pytest
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# -----------------------------------------------------------------------------
# Toplevel GPIO Operation Decoder Wrapper
# -----------------------------------------------------------------------------
class GPIO_OPERATION_DECODER(lib.Entity):
    """This class connects the GPIO_OPERATION_DECODER entity to the test framework."""
    _package = GENERICS

    address = lib.Entity.Input_pin
    write   = lib.Entity.Input_pin

    wr_en   = lib.Entity.Output_pin  # 7 bits
    wr_op   = lib.Entity.Output_pin  # 2 bits
    rd_sel  = lib.Entity.Output_pin  # 3 bits

# -----------------------------------------------------------------------------
# Address map — matches the VHDL decoder
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
    "wr_irq_clr":    "1011",  # ← updated to match decoder

    "rd_dir":        "1000",
    "rd_out":        "1001",
    "rd_pins":       "1010",
    "rd_irq_stat":   "1011",
    "rd_irq_mask":   "1100",
    "rd_rise_mask":  "1101",
    "rd_fall_mask":  "1110",
    "nop":           "1111",
}

# -----------------------------------------------------------------------------
# Stimulus helper
# -----------------------------------------------------------------------------
async def dec_op(dut, trace, op, write=False):
    dut.address.value = BinaryValue(ADDR[op], n_bits=4)
    dut.write.value = BinaryValue('1' if write else '0')
    await trace.cycle()
    dut.write.value = BinaryValue('0')

# -----------------------------------------------------------------------------
# Write decoding test cases
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

# -----------------------------------------------------------------------------
# Read decoding test cases
# -----------------------------------------------------------------------------
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
# Functional test
# -----------------------------------------------------------------------------
@GPIO_OPERATION_DECODER.testcase
async def tb_operation_decoder_manual(dut: GPIO_OPERATION_DECODER, trace: lib.Waveform):
    """Verifies write and read decoding logic from the VHDL decoder."""
    for name, bit_i, exp_wr_op in WRITE_CASES:
        await dec_op(dut, trace, name, write=True)
        exp_wr_en = format(1 << bit_i, '07b')
        yield trace.check(dut.wr_en, exp_wr_en, f"wr_en mismatch for {name}")
        yield trace.check(dut.wr_op, exp_wr_op, f"wr_op mismatch for {name}")

    for name, exp_rd_sel in READ_CASES:
        await dec_op(dut, trace, name, write=False)
        yield trace.check(dut.rd_sel, exp_rd_sel, f"rd_sel mismatch for {name}")
        if name == "rd_irq_stat":
            yield trace.check(dut.wr_en, "1000000", f"wr_en should be 0 during read: {name}")
        else:
            yield trace.check(dut.wr_en, "0000000", f"wr_en should be 0 during read: {name}")

# -----------------------------------------------------------------------------
# Synthesis check
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_GPIO_OPERATION_DECODER_synthesis():
    GPIO_OPERATION_DECODER.build_vhd()
    GPIO_OPERATION_DECODER.build_netlistsvg()

# -----------------------------------------------------------------------------
# Test run wrapper
# -----------------------------------------------------------------------------
@pytest.mark.testcases
def test_gpio_operation_decoder_manual():
    GPIO_OPERATION_DECODER.test_with(tb_operation_decoder_manual)

# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    lib.run_test(__file__)
