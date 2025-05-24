import pytest
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# -----------------------------------------------------------------------------
# Toplevel GPIO Operation Decoder Wrapper
# -----------------------------------------------------------------------------
class GPIO_OPERATION_DECODER(lib.Entity):
    _package = GENERICS

    address = lib.Entity.Input_pin
    write   = lib.Entity.Input_pin
    read    = lib.Entity.Input_pin

    wr_en   = lib.Entity.Output_pin  # 7 bits
    wr_op   = lib.Entity.Output_pin  # 2 bits
    rd_sel  = lib.Entity.Output_pin  # 3 bits

# -----------------------------------------------------------------------------
# Address map — matches the NEW VHDL decoder
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

    "rd_dir":        "0000",  # same as wr_dir
    "rd_out_load":   "0001",
    "rd_out_set":    "0010",
    "rd_out_clear":  "0011",
    "rd_out_toggle": "0100",

    "rd_irq_mask":   "0101",
    "rd_rise_mask":  "0110",
    "rd_fall_mask":  "0111",
    "rd_irq_stat":   "1000",
    "rd_pins":       "1001",
    "nop":           "1111"
}

# -----------------------------------------------------------------------------
# Stimulus helper
# -----------------------------------------------------------------------------
async def dec_op(dut, trace, op, write=False):
    dut.address.value = BinaryValue(ADDR[op], n_bits=4)
    dut.write.value = BinaryValue('1' if write else '0')
    dut.read.value = BinaryValue('1' if not write else '0')
    await trace.cycle()
    dut.write.value = BinaryValue('0')
    dut.read.value = BinaryValue('0')

# -----------------------------------------------------------------------------
# Write decoding test cases (name, wr_en bit, wr_op value)
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
]

# -----------------------------------------------------------------------------
# Read decoding test cases (name, rd_sel value, wr_en expected value)
# -----------------------------------------------------------------------------
READ_CASES = [
    ("rd_dir",         "000", "0000000"),
    ("rd_out_load",    "001", "0000000"),
    ("rd_out_set",     "001", "0000000"),
    ("rd_out_clear",   "001", "0000000"),
    ("rd_out_toggle",  "001", "0000000"),
    ("rd_pins",        "010", "0000000"),
    ("rd_irq_stat",    "011", "1000000"),  # IRQ_CLR
    ("rd_irq_mask",    "100", "0000000"),
    ("rd_rise_mask",   "101", "0000000"),
    ("rd_fall_mask",   "110", "0000000"),
    ("nop",            "111", "0000000"),
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

    for name, exp_rd_sel, exp_wr_en in READ_CASES:
        await dec_op(dut, trace, name, write=False)
        yield trace.check(dut.rd_sel, exp_rd_sel, f"rd_sel mismatch for {name}")
        yield trace.check(dut.wr_en, exp_wr_en, f"wr_en mismatch for read: {name}")

# -----------------------------------------------------------------------------
# Synthesis check
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_GPIO_OPERATION_DECODER_synthesis():
    GPIO_OPERATION_DECODER.build_vhd()

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
