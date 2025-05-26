# test_TIMER.py
# =============================================================================
# Functional test-bench for the VHDL entity: TIMER
# =============================================================================

import pytest
import lib
from test_GENERICS_package import GENERICS
from cocotb.binary import BinaryValue

# -----------------------------------------------------------------------------
# Python-to-VHDL wrapper
# -----------------------------------------------------------------------------
class TIMER(lib.Entity):
    _package = GENERICS

    clock   = lib.Entity.Input_pin
    clear   = lib.Entity.Input_pin
    data_in = lib.Entity.Input_pin
    address = lib.Entity.Input_pin
    write   = lib.Entity.Input_pin
    read    = lib.Entity.Input_pin

    data_out = lib.Entity.Output_pin
    irq      = lib.Entity.Output_pin
    pwm      = lib.Entity.Output_pin

# -----------------------------------------------------------------------------
# Address maps (3-bit address space)
# -----------------------------------------------------------------------------
WR = dict(
    config=0x0,         # Combined start/mode/pwm_en/irq_mask
    load_timer=0x1,
    reset=0x2,
    load_top=0x3,
    load_duty=0x4,
    load_prescaler=0x7 
)
RD = dict(
    timer=0x1,
    top=0x3,
    duty=0x4,
    configs=0x0,
    pwm=0x6,
    ovf_status=0x5,
    prescaler=0x7     
)

# -----------------------------------------------------------------------------
# Helper: binary vector conversion
# -----------------------------------------------------------------------------
def bv(val: int, width: int = 32):
    return BinaryValue(value=val, n_bits=width, bigEndian=False)

# -----------------------------------------------------------------------------
# Helper: decode config vector into individual bits
# [irq_mask, pwm_en, mode, start] → bits 3..0
# -----------------------------------------------------------------------------
def decode_cfg(vec: BinaryValue):
    v = int(vec)
    start    = (v >> 0) & 1
    mode     = (v >> 1) & 1
    pwm_en   = (v >> 2) & 1
    irq_mask = (v >> 3) & 1
    return start, mode, pwm_en, irq_mask

# -----------------------------------------------------------------------------
# Write Operation
# -----------------------------------------------------------------------------
async def bus_write(dut, trace, addr, value):
    dut.address.value = bv(addr, 3)
    dut.data_in.value = bv(value, 32)
    dut.write.value   = BinaryValue("1")
    await trace.cycle()
    dut.write.value   = BinaryValue("0")
    dut.data_in.value = bv(0, 32)

# -----------------------------------------------------------------------------
# Read Operation
# -----------------------------------------------------------------------------
async def bus_read(dut, trace, addr):
    dut.address.value = bv(addr, 3)
    dut.read.value    = BinaryValue("1")
    await trace.cycle()
    dut.read.value    = BinaryValue("0")

# -----------------------------------------------------------------------------
# Test Case: Timer in Hold Mode
# -----------------------------------------------------------------------------
@TIMER.testcase
async def tb_timer_hold(dut: TIMER, trace: lib.Waveform):
    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")

    # Write config bits [irq_mask, pwm_en, mode, start] = 1000b = 0x8
    await bus_write(dut, trace, WR["config"], 0b1000)
    await bus_write(dut, trace, WR["config"], 0b1010)  # irq_mask + mode

    await bus_read(dut, trace, RD["configs"])
    yield trace.check(dut.data_out, bv(0b1010, 32), "Config = irq_mask=1, pwm_en=0, mode=1, start=0")

    await bus_write(dut, trace, WR["load_timer"], 0xFFFFFFFC)
    await bus_read(dut, trace, RD["timer"])
    yield trace.check(dut.data_out, bv(0xFFFFFFFC, 32), "Timer = 0xFFFFFFFC")

    await bus_write(dut, trace, WR["config"], 0b1011)  # start=1
    await bus_read(dut, trace, RD["timer"])
    yield trace.check(dut.data_out, bv(0xFFFFFFFD, 32), "Timer = 0xFFFFFFFD")

    await trace.cycle(10)
    await bus_read(dut, trace, RD["timer"])
    yield trace.check(dut.data_out, bv(0xFFFFFFFF, 32), "Timer = 0xFFFFFFFF")
    yield trace.check(dut.irq, BinaryValue("1"), "IRQ should be high")

    await bus_read(dut, trace, RD["ovf_status"])
    yield trace.check(dut.data_out, bv(1, 32), "IRQ status = 1")
    yield trace.check(dut.irq, BinaryValue("0"), "IRQ cleared")

    await bus_write(dut, trace, WR["load_top"], 0xF)
    await bus_read(dut, trace, RD["top"])
    yield trace.check(dut.data_out, bv(0xF, 32), "Top = 0xF")

    await bus_write(dut, trace, WR["reset"], 0)
    for _ in range(20):
        await trace.cycle()

    await bus_read(dut, trace, RD["timer"])
    yield trace.check(dut.data_out, bv(0xF, 32), "Timer = 0xF")
    yield trace.check(dut.irq, BinaryValue("1"), "IRQ should be high")

    await bus_read(dut, trace, RD["ovf_status"])
    yield trace.check(dut.data_out, bv(1, 32), "IRQ status = 1")
    yield trace.check(dut.irq, BinaryValue("0"), "IRQ cleared")

# -----------------------------------------------------------------------------
# Test Case: Timer in Wrap-Around Mode
# -----------------------------------------------------------------------------
@TIMER.testcase
async def tb_timer_wrap(dut: TIMER, trace: lib.Waveform):
    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")

    await bus_write(dut, trace, WR["config"], 0b0100)  # pwm_en
    await bus_write(dut, trace, WR["config"], 0b0100)  # keep pwm_en

    await bus_read(dut, trace, RD["configs"])
    yield trace.check(dut.data_out, bv(0b0100, 32), "Config = pwm_en=1")

    await bus_write(dut, trace, WR["load_top"], 0xF)
    await bus_read(dut, trace, RD["top"])
    yield trace.check(dut.data_out, bv(0xF, 32), "Top = 0xF")

    await bus_write(dut, trace, WR["load_duty"], 0x8)
    await bus_read(dut, trace, RD["duty"])
    yield trace.check(dut.data_out, bv(0x8, 32), "Duty = 0x8")

    await bus_read(dut, trace, RD["pwm"])
    yield trace.check(dut.data_out, bv(1, 32), "PWM = 1")

    await bus_write(dut, trace, WR["config"], 0b0101)  # pwm_en + start

    for i in range(7):
        await bus_read(dut, trace, RD["timer"])
        yield trace.check(dut.data_out, bv(1 + i, 32), f"Timer = {1 + i}")
        yield trace.check(dut.pwm, BinaryValue("1"), "PWM = 1")

    for i in range(8):
        await bus_read(dut, trace, RD["timer"])
        yield trace.check(dut.data_out, bv(8 + i, 32), f"Timer = {8 + i}")
        yield trace.check(dut.pwm, BinaryValue("0"), "PWM = 0")

    for i in range(8):
        await bus_read(dut, trace, RD["timer"])
        yield trace.check(dut.data_out, bv(i, 32), f"Timer = {i}")
        yield trace.check(dut.pwm, BinaryValue("1"), "PWM = 1")


@TIMER.testcase
async def tb_timer_prescaler(dut: TIMER, trace: lib.Waveform):
    """Test prescaler: configure it, read it back, and verify the timer slows down."""

    # -----------------------------------------------------------------------------
    # Initial reset to ensure clean state
    # -----------------------------------------------------------------------------
    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")
    await trace.cycle()

    # -----------------------------------------------------------------------------
    # Step 1: Set prescaler to 4 → tick every 5 clock cycles
    # -----------------------------------------------------------------------------
    await bus_write(dut, trace, WR["load_prescaler"], 4)

    # -----------------------------------------------------------------------------
    # Step 2: Read back the prescaler value and validate
    # -----------------------------------------------------------------------------
    await bus_read(dut, trace, RD["prescaler"])
    yield trace.check(dut.data_out, bv(4), "Prescaler should be 4")

    # -----------------------------------------------------------------------------
    # Step 3: Load timer with 0 and set TOP = 10
    # -----------------------------------------------------------------------------
    await bus_write(dut, trace, WR["load_timer"], 0)
    await bus_write(dut, trace, WR["load_top"], 100)

    # -----------------------------------------------------------------------------
    # Step 4: Start the timer in wrap-around mode (start=1, mode=0)
    # -----------------------------------------------------------------------------
    await bus_write(dut, trace, WR["config"], 0b0001)

    # Normalize cycle count to ensure we start from a known state (e.g., counter = 1)
    await trace.cycle(2)

    # -----------------------------------------------------------------------------
    # Step 5: Observe that timer increments only every 5 cycles (due to prescaler)
    # -----------------------------------------------------------------------------
    for i in range(50):
        # Wait 3 cycles to account for prescaler
        await trace.cycle(3) 
        # Read timer value (includes a cycle in the operation)
        await bus_read(dut, trace, RD["timer"])
        # Check that the timer value is still i in the first 4 cycles
        yield trace.check(dut.data_out, bv(i + 1, 32), f"Timer should still be {i} after 3 cycles")
        # Read the timer again to confirm it increments
        await bus_read(dut, trace, RD["timer"])
        # Check that the timer value is now i + 2 (due to being the 5th cycle)
        yield trace.check(dut.data_out, bv(i + 2, 32), f"Timer should now be {i}")



# -----------------------------------------------------------------------------
# Synthesis smoke-check
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_TIMER_synthesis():
    TIMER.build_vhd()

# -----------------------------------------------------------------------------
# Pytest entry point
# -----------------------------------------------------------------------------

@pytest.mark.testcases
def test_timer_prescaler():
    TIMER.test_with(tb_timer_prescaler)


if __name__ == "__main__":
    lib.run_test(__file__)
