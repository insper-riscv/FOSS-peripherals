'''
# =========================== OUTPUT-MODE TEST ===========================
import pytest
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# ----------------------------------------------------------------------------
# Wrapper: GPIO cell seen as OUTPUT (pin driven by DUT)
# ----------------------------------------------------------------------------
class GPIO_CELL(lib.Entity):
    _package = GENERICS

    clock      = lib.Entity.Input_pin
    clear      = lib.Entity.Input_pin
    data_in    = lib.Entity.Input_pin
    wr_signals = lib.Entity.Input_pin
    wr_op      = lib.Entity.Input_pin
    data_out   = lib.Entity.Output_pin
    gpio_pin   = lib.Entity.Output_pin

# ----------------------------------------------------------------------------
# Operation Constants
# ----------------------------------------------------------------------------
LOAD   = "00"
SET    = "01"
CLEAR  = "10"
TOGGLE = "11"

WR_DIR  = 0
WR_LOAD = 1
WR_BIT  = 2

# ----------------------------------------------------------------------------
# Helper function to convert bit index to one-hot encoding
# ----------------------------------------------------------------------------
def onehot(bit: int) -> str:
    return format(1 << bit, "07b")

# ----------------------------------------------------------------------------
# Helper function to write to GPIO
# ----------------------------------------------------------------------------
async def write_gpio(dut, trace, wr_bit, op_code, data):
    dut.data_in.value = BinaryValue(str(data))
    dut.wr_signals.value = BinaryValue(onehot(wr_bit))
    dut.wr_op.value = BinaryValue(op_code)
    await trace.cycle()
    dut.wr_signals.value = BinaryValue("0000000")
    dut.wr_op.value = BinaryValue("00")
    dut.data_in.value = BinaryValue("0")
    await trace.cycle()
    await trace.cycle()

# ----------------------------------------------------------------------------
# Test case: GPIO cell as output
# ----------------------------------------------------------------------------
@GPIO_CELL.testcase
async def tb_gpio_cell_output(dut: GPIO_CELL, trace: lib.Waveform):
    # Reset
    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")

    # Step 1: Set direction to output
    await write_gpio(dut, trace, WR_DIR, LOAD, 1)
    yield trace.check(dut.data_out, "0000001", "Step 1: Direction register should be 1")
    yield trace.check(dut.gpio_pin, "0", "Step 1: Pin should be high impedance")

    # Step 2: LOAD 0 → pin LOW
    await write_gpio(dut, trace, WR_LOAD, LOAD, 0)
    yield trace.check(dut.gpio_pin, "0", "Step 2: GPIO pin should be LOW")
    yield trace.check(dut.data_out, "0000001", "Step 2: Data out check")

    # Step 3: SET → pin HIGH
    await write_gpio(dut, trace, WR_BIT, SET, 1)
    yield trace.check(dut.gpio_pin, "1", "Step 3: GPIO pin should be HIGH")
    yield trace.check(dut.data_out, "0000111", "Step 3: Data out check")

    # Step 4: CLEAR → pin LOW
    await write_gpio(dut, trace, WR_BIT, CLEAR, 1)
    yield trace.check(dut.gpio_pin, "0", "Step 4: GPIO pin should be LOW")
    yield trace.check(dut.data_out, "0000001", "Step 4: Data out check")

    # Step 5: TOGGLE → pin HIGH
    await write_gpio(dut, trace, WR_BIT, TOGGLE, 1)
    yield trace.check(dut.gpio_pin, "1", "Step 5: GPIO pin should be HIGH")
    yield trace.check(dut.data_out, "0000111", "Step 5: Data out check")

    # Step 6: Disable output
    await write_gpio(dut, trace, WR_DIR, LOAD, 0)
    yield trace.check(dut.data_out, "0000Z10", "Step 6: Direction register should be 0")
    yield trace.check(dut.gpio_pin, "Z", "Step 6: GPIO pin should be high impedance")
    # Step 7: LOAD 1 → pin HIGH
    await write_gpio(dut, trace, WR_LOAD, LOAD, 1)
    yield trace.check(dut.gpio_pin, "Z", "Step 7: GPIO pin should be high impedance")
    yield trace.check(dut.data_out, "0000Z10", "Step 7: Data out check")


# ----------------------------------------------------------------------------
# Synthesis test
# ----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_GPIO_CELL_synthesis():
    GPIO_CELL.build_vhd()
    GPIO_CELL.build_netlistsvg()

# ----------------------------------------------------------------------------
# Test execution
# ----------------------------------------------------------------------------
@pytest.mark.testcases
def test_gpio_cell_output():
    GPIO_CELL.test_with(tb_gpio_cell_output)

if __name__ == "__main__":
    lib.run_test(__file__)
'''
# =========================== INPUT-MODE & IRQ TEST ===========================
import pytest
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# ----------------------------------------------------------------------------
# Wrapper: GPIO cell seen as INPUT (pin driven by Python TB, read by DUT)
# ----------------------------------------------------------------------------
class GPIO_CELL(lib.Entity):
    _package = GENERICS

    clock      = lib.Entity.Input_pin
    clear      = lib.Entity.Input_pin
    data_in    = lib.Entity.Input_pin
    wr_signals = lib.Entity.Input_pin  # 7-bit vector (wr_en)
    wr_op      = lib.Entity.Input_pin
    data_out   = lib.Entity.Output_pin
    gpio_pin   = lib.Entity.Input_pin

# ----------------------------------------------------------------------------
# Operation constants
# ----------------------------------------------------------------------------
LOAD   = "00"
WR_DIR       = 0
WR_IRQ_MASK  = 3
WR_RISE_MASK = 4
WR_FALL_MASK = 5
WR_IRQ_CLR   = 6  # <- mapped to read of IRQ status ("1011")

# ----------------------------------------------------------------------------
# Helper functions	
# ----------------------------------------------------------------------------
def onehot(bit: int) -> str:
    return format(1 << bit, "07b")

async def write_register(dut, trace, bit_index, value="1"):
    dut.data_in.value = BinaryValue(value)
    dut.wr_signals.value = BinaryValue(onehot(bit_index))
    await trace.cycle()
    dut.wr_signals.value = BinaryValue("0000000")
    dut.data_in.value = BinaryValue("0")
    await trace.cycle()

async def read_and_clear_irq(dut, trace):
    """Simulates a read that clears IRQ by asserting wr_signals(6)."""
    dut.wr_signals.value = BinaryValue(onehot(WR_IRQ_CLR))
    await trace.cycle()
    dut.wr_signals.value = BinaryValue("0000000")
    await trace.cycle()

async def set_pin(dut, trace, value):
    dut.gpio_pin.value = BinaryValue(str(value))
    for _ in range(3):
        await trace.cycle()

# ----------------------------------------------------------------------------
# Test case: GPIO cell as input with IRQ
# ----------------------------------------------------------------------------
@GPIO_CELL.testcase
async def tb_gpio_cell_input_irq(dut: GPIO_CELL, trace: lib.Waveform):
    # Reset
    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")

    # Step 1: Set direction to input
    await write_register(dut, trace, WR_DIR, "0")
    yield trace.check(dut.data_out, "0000Z00", "Step 1: dir=0, all other regs cleared")

    # Step 2: Enable all interrupts
    await write_register(dut, trace, WR_IRQ_MASK)
    await write_register(dut, trace, WR_RISE_MASK)
    await write_register(dut, trace, WR_FALL_MASK)
    yield trace.check(dut.data_out, "0111Z00", "Step 2: All IRQ masks set")

    # Step 3: Pin LOW initially, no IRQ
    await set_pin(dut, trace, 0)
    yield trace.check(dut.data_out, "0111000", "Step 3: Pin LOW, no interrupt")

    # Step 4: Rising edge, should trigger IRQ
    await set_pin(dut, trace, 1)
    yield trace.check(dut.data_out, "1111100", "Step 4: Rising edge triggered IRQ")

    # Step 5: Read to clear IRQ
    await read_and_clear_irq(dut, trace)
    yield trace.check(dut.data_out, "0111100", "Step 5: IRQ cleared after read")

    # Step 6: Falling edge, should trigger IRQ
    await set_pin(dut, trace, 0)
    yield trace.check(dut.data_out, "1111000", "Step 6: Falling edge triggered IRQ")

    # Step 7: Read to clear and disable rising mask
    await read_and_clear_irq(dut, trace)
    await write_register(dut, trace, WR_RISE_MASK, "0")
    yield trace.check(dut.data_out, "0101000", "Step 7: IRQ cleared, rise mask disabled")

    # Step 8: Rising edge ignored
    await set_pin(dut, trace, 1)
    yield trace.check(dut.data_out, "0101100", "Step 8: Rising edge ignored (mask off)")

    # Step 9: Disable IRQ mask globally, falling still masked
    await write_register(dut, trace, WR_IRQ_MASK, "0")
    await set_pin(dut, trace, 0)
    yield trace.check(dut.data_out, "0100000", "Step 9: IRQ globally disabled")

# ----------------------------------------------------------------------------
# Synthesis test
# ----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_GPIO_CELL_synthesis():
    GPIO_CELL.build_vhd()

# ----------------------------------------------------------------------------
# Test execution
# ----------------------------------------------------------------------------
@pytest.mark.testcases
def test_gpio_cell_input_irq():
    GPIO_CELL.test_with(tb_gpio_cell_input_irq)

if __name__ == "__main__":
    lib.run_test(__file__)

