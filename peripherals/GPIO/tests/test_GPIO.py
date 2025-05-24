'''
# =========================== GPIO – OUTPUT‑MODE TEST ===========================
import pytest
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# -----------------------------------------------------------------------------
# DUT wrapper
# -----------------------------------------------------------------------------
class GPIO(lib.Entity):
    _package = GENERICS                # generic helper

    clock     = lib.Entity.Input_pin
    clear     = lib.Entity.Input_pin
    data_in   = lib.Entity.Input_pin
    address   = lib.Entity.Input_pin
    write     = lib.Entity.Input_pin
    read      = lib.Entity.Input_pin

    data_out  = lib.Entity.Output_pin
    irq       = lib.Entity.Output_pin
    gpio_pins = lib.Entity.Output_pin   # DUT drives the pins in this test

# -----------------------------------------------------------------------------
# Address map (matches VHDL decoder)
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
# Helper utilities ------------------------------------------------------------
# -----------------------------------------------------------------------------
def bin_val(value: int, width: int) -> BinaryValue:
    return BinaryValue(format(value, f"0{width}b"))

async def bus_write(dut, trace, addr_key: str, data: int):
    width = len(dut.data_in)
    dut.address.value = BinaryValue(ADDR[addr_key])
    dut.data_in.value = bin_val(data, width)
    dut.write.value   = BinaryValue("1")
    await trace.cycle()
    dut.write.value   = BinaryValue("0")
    dut.data_in.value = bin_val(0, width)          # drive zeros of correct width

async def bus_read(dut, trace, addr_key: str):
    """Performs a read; data appears on dut.data_out the cycle after read strobe."""
    dut.address.value = BinaryValue(ADDR[addr_key])
    dut.read.value    = BinaryValue("1")
    await trace.cycle()
    dut.read.value    = BinaryValue("0")

# -----------------------------------------------------------------------------
# Test‑case -------------------------------------------------------------------
# -----------------------------------------------------------------------------
@GPIO.testcase
async def tb_gpio_output(dut: GPIO, trace: lib.Waveform):
    """Drives the top-level GPIO in OUTPUT mode and checks datapath + readback."""
    WIDTH = len(dut.data_in)
    HALF = WIDTH // 2

    # Reset
    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")

    # DIR → OUTPUT (only lower half enabled)
    dir_mask = (1 << HALF) - 1  # 0x00FF for WIDTH=16
    await bus_write(dut, trace, "wr_dir", dir_mask)
    await bus_read(dut, trace, "rd_dir")
    yield trace.check(dut.data_out, format(dir_mask, f"0{WIDTH}b"), "DIR should be lower half only")
    yield trace.check(dut.gpio_pins, ("0" * HALF + "Z" * HALF)[::-1], "Pins: lower LOW, upper Z")

    # LOAD 0x0
    await bus_write(dut, trace, "wr_out_load", 0)
    await bus_read(dut, trace, "rd_out")
    yield trace.check(dut.data_out, "0" * WIDTH, "OUT = 0 after LOAD")
    yield trace.check(dut.gpio_pins, ("0" * HALF + "Z" * HALF)[::-1], "Pins LOW (lower), Z (upper)")

    # SET pattern 0b0101...
    pattern_set = int("01" * HALF, 2)
    await bus_write(dut, trace, "wr_out_set", pattern_set)
    await bus_read(dut, trace, "rd_out")
    expected_set = format(pattern_set, f"0{WIDTH}b")
    yield trace.check(dut.data_out, expected_set, "OUT after SET")
    yield trace.check(dut.gpio_pins, "Z" * HALF + expected_set[-HALF:], "Pins reflect SET (lower half)")

    # CLEAR bit 1
    await bus_write(dut, trace, "wr_out_clear", 1 << 1)
    await bus_read(dut, trace, "rd_out")
    expected_clear = list(expected_set)
    expected_clear[-2] = '0'
    expected_clear = ''.join(expected_clear)
    yield trace.check(dut.data_out, expected_clear, "Bit 1 cleared")
    yield trace.check(dut.gpio_pins, "Z" * HALF + expected_clear[-HALF:], "Pins reflect CLEAR")

    # TOGGLE
    toggle_mask = 0xF
    await bus_write(dut, trace, "wr_out_toggle", toggle_mask)
    await bus_read(dut, trace, "rd_out")
    toggled = int(expected_clear, 2) ^ toggle_mask
    expected_toggle = format(toggled, f"0{WIDTH}b")
    yield trace.check(dut.data_out, expected_toggle, "Toggle applied")
    yield trace.check(dut.gpio_pins, "Z" * HALF + expected_toggle[-HALF:], "Pins reflect TOGGLE")

    # IRQ must remain LOW
    yield trace.check(dut.irq, "0", "IRQ must stay low in output test")




# -----------------------------------------------------------------------------
# Synthesis / CI hooks --------------------------------------------------------
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_GPIO_synth():
    GPIO.build_vhd()

@pytest.mark.testcases
def test_gpio_output():
    GPIO.test_with(tb_gpio_output)

if __name__ == "__main__":
    lib.run_test(__file__)'''

import pytest
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# ----------------------------------------------------------------------------
# Wrapper: GPIO top-level peripheral
# ----------------------------------------------------------------------------
class GPIO(lib.Entity):
    _package = GENERICS
    _generics = dict(DATA_WIDTH=32)

    clock     = lib.Entity.Input_pin
    clear     = lib.Entity.Input_pin
    data_in   = lib.Entity.Input_pin
    address   = lib.Entity.Input_pin
    write     = lib.Entity.Input_pin
    read      = lib.Entity.Input_pin

    data_out  = lib.Entity.Output_pin
    irq       = lib.Entity.Output_pin
    gpio_pins = lib.Entity.Input_pin  # TB drives the input pins

# ----------------------------------------------------------------------------
# Address map
# ----------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------
# Bus helpers
# ----------------------------------------------------------------------------
def bin32(val: int) -> BinaryValue:
    return BinaryValue(format(val, "032b"))

async def bus_write(dut, trace, addr_key, data):
    dut.address.value = BinaryValue(ADDR[addr_key])
    dut.data_in.value = bin32(data)
    dut.write.value   = BinaryValue("1")
    await trace.cycle()
    dut.write.value   = BinaryValue("0")
    dut.data_in.value = bin32(0)
    await trace.cycle()

async def bus_read(dut, trace, addr_key):
    dut.address.value = BinaryValue(ADDR[addr_key])
    dut.read.value    = BinaryValue("1")
    await trace.cycle()
    dut.read.value    = BinaryValue("0")
    await trace.cycle()

# ----------------------------------------------------------------------------
# Testcase
# ----------------------------------------------------------------------------
@GPIO.testcase
async def tb_gpio_input_irq(dut: GPIO, trace: lib.Waveform):
    # Reset
    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")

    # Set all pins to input (dir=0)
    await bus_write(dut, trace, "wr_dir", 0x00000000)

    # Enable all interrupts and edge masks
    await bus_write(dut, trace, "wr_irq_mask",  0xFFFFFFFF)
    await bus_write(dut, trace, "wr_rise_mask", 0xFFFFFFFF)
    await bus_write(dut, trace, "wr_fall_mask", 0xFFFFFFFF)

    # Drive pins low, no IRQ should be raised
    dut.gpio_pins.value = bin32(0x00000000)
    for _ in range(3):
        await trace.cycle()
    yield trace.check(dut.irq, "0", "Initial LOW, no IRQ")

   # Rising edge on pin0
    dut.gpio_pins.value = bin32(0x00000001)
    for _ in range(3):
        await trace.cycle()
    yield trace.check(dut.irq, "1", "IRQ on rising edge")

    # Clear IRQ
    await bus_read(dut, trace, "rd_irq_stat")
    await trace.cycle()
    yield trace.check(dut.irq, "0", "IRQ cleared after read")

    # Extra cycle to update previous pin state
    await trace.cycle()

    # Falling edge on pin0
    dut.gpio_pins.value = bin32(0x00000000)
    for _ in range(3):
        await trace.cycle()
    yield trace.check(dut.irq, "1", "IRQ on falling edge")


    # Clear IRQ
    await bus_read(dut, trace, "rd_irq_stat")
    await trace.cycle()
    yield trace.check(dut.irq, "0", "IRQ cleared after second read")

    # Disable global mask → no IRQs triggered
    await bus_write(dut, trace, "wr_irq_mask", 0x00000000)
    dut.gpio_pins.value = bin32(0x00000001)
    for _ in range(3):
        await trace.cycle()
    yield trace.check(dut.irq, "0", "IRQ must stay low with mask=0")

# ----------------------------------------------------------------------------
# Pytest hooks
# ----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_GPIO_synth():
    GPIO.build_vhd()

@pytest.mark.testcases
def test_gpio_input_irq():
    GPIO.test_with(tb_gpio_input_irq)

if __name__ == "__main__":
    lib.run_test(__file__)