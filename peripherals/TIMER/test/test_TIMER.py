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
    pwm     = lib.Entity.Output_pin

# -----------------------------------------------------------------------------
# Address maps
# -----------------------------------------------------------------------------
WR = dict(start_stop=0x0, mode=0x1, pwm_en=0x2, load_timer=0x3,
          load_top=0x4, load_duty=0x5, irq_mask=0x6, reset=0x7)
RD = dict(timer=0x8, top=0x9, duty=0xA, configs=0xB,
          pwm=0xC, ovf_status=0xD)

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
    dut.address.value = bv(addr, 4)
    dut.data_in.value = bv(value, 32)
    dut.write.value   = BinaryValue("1")
    await trace.cycle()
    dut.write.value   = BinaryValue("0")
    dut.data_in.value = bv(0, 32)

# -----------------------------------------------------------------------------
# Read Operation
# -----------------------------------------------------------------------------
async def bus_read(dut, trace, addr):
    dut.address.value = bv(addr, 4)
    dut.read.value    = BinaryValue("1")
    await trace.cycle()
    dut.read.value    = BinaryValue("0")

# -----------------------------------------------------------------------------
# Test Case: Timer in Hold Mode
# -----------------------------------------------------------------------------
@TIMER.testcase
async def tb_timer_hold(dut: TIMER, trace: lib.Waveform):
    # Step 1: Reset
    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")

    # Step 2: Write IRQ Mask and enable hold mode
    await bus_write(dut, trace, WR["irq_mask"], 1)
    await bus_write(dut, trace, WR["mode"], 1)

    # Step 3: Read Configs and decode
    await bus_read(dut, trace, RD["configs"])
    yield trace.check(dut.data_out, bv(0b00001010, 32), "Config bits = irq_mask=1, pwm_en=0, mode=1, start=0")

    # Step 4: Load Timer Close to Overflow and Read Timer Value to Verify
    await bus_write(dut, trace, WR["load_timer"], 0xFFFFFFFC)
    await bus_read(dut, trace, RD["timer"])
    yield trace.check(dut.data_out, bv(0xFFFFFFFC, 32), "Timer value = 0xFFFFFFFD")

    # Step 5: Start Timer and Read Timer Value to Verify
    await bus_write(dut, trace, WR["start_stop"], 1)
    await bus_read(dut, trace, RD["timer"])
    yield trace.check(dut.data_out, bv(0xFFFFFFFD, 32), "Timer value = 0xFFFFFFFD")

    # Step 6: Check if Timer is on Hold after Wrap-Around and if IRQ was Triggered.
    await trace.cycle(10)
    await bus_read(dut, trace, RD["timer"])
    yield trace.check(dut.data_out, bv(0xFFFFFFFF, 32), "Timer value = 0xFFFFFFFF")
    yield trace.check(dut.irq, BinaryValue("1"), "IRQ should be triggered")
    yield trace.check(dut.pwm, BinaryValue("Z"), "PWM should be Z")

    # Step 7: Read IRQ Status and check if it clears the IRQ
    await bus_read(dut, trace, RD["ovf_status"])
    yield trace.check(dut.data_out, bv(0x00000001, 32), "IRQ status should be 1")
    yield trace.check(dut.irq, BinaryValue("0"), "IRQ should be cleared")
    yield trace.check(dut.pwm, BinaryValue("Z"), "PWM should be Z")

    # Step 8: Set a new Top value
    await bus_write(dut, trace, WR["load_top"], 0x0000000F)
    await bus_read(dut, trace, RD["top"])
    yield trace.check(dut.data_out, bv(0x0000000F, 32), "Top value = 0x0000000F")
    # Step 9: Restart Timer and wait for it to reach the new Top value
    await bus_write(dut, trace, WR["reset"], 0)
    for i in range(20):
        await trace.cycle()
   # Step 10: Assert that Timer is on hold and IRQ is triggered
    await bus_read(dut, trace, RD["timer"])
    yield trace.check(dut.data_out, bv(0x0000000F, 32), "Timer value = 0x0000000F")
    yield trace.check(dut.irq, BinaryValue("1"), "IRQ should be triggered")
    yield trace.check(dut.pwm, BinaryValue("Z"), "PWM should be Z")

    # Step 11: Read IRQ Status and check if it clears the IRQ
    await bus_read(dut, trace, RD["ovf_status"])
    yield trace.check(dut.data_out, bv(0x00000001, 32), "IRQ status should be 1")
    yield trace.check(dut.irq, BinaryValue("0"), "IRQ should be cleared")
    yield trace.check(dut.pwm, BinaryValue("Z"), "PWM should be Z")

    
    
# -----------------------------------------------------------------------------
# Test Case: Timer in Wrap-Around Mode
# -----------------------------------------------------------------------------
@TIMER.testcase
async def tb_timer_wrap(dut: TIMER, trace: lib.Waveform):
    # Step 1: Reset
    dut.clear.value = BinaryValue("1")
    await trace.cycle()
    dut.clear.value = BinaryValue("0")

    # Step 2: Write PWM enable and wrap-around mode
    await bus_write(dut, trace, WR["pwm_en"], 1)
    await bus_write(dut, trace, WR["mode"], 0)

    # Step 3: Read Configs and decode
    await bus_read(dut, trace, RD["configs"])
    yield trace.check(dut.data_out, bv(0b00000100, 32), "Config bits = irq_mask=0, pwm_en=1, mode=0, start=0")

    # Step 4: Set Top value and assert it
    await bus_write(dut, trace, WR["load_top"], 0x0000000F)
    await bus_read(dut, trace, RD["top"])
    yield trace.check(dut.data_out, bv(0x0000000F, 32), "Top value = 0x0000000F")
    # Step 4: Load Duty value of 50% and assert it
    await bus_write(dut, trace, WR["load_duty"], 0x00000008)
    await bus_read(dut, trace, RD["duty"])
    yield trace.check(dut.data_out, bv(0x00000008, 32), "Duty value = 0x00000008")
    # Step 5: Start Timer and assert that PWM is High until 50% of the Top value
    # Checa função de leitura do PWM
    await bus_read(dut, trace, RD["pwm"])
    yield trace.check(dut.data_out, bv(0x00000001, 32), " PWM value = 0x00000001")
    await bus_write(dut, trace, WR["start_stop"], 1)
    # Starts at 0x00000001 because of the start operation
    for i in range(7):
        await bus_read(dut, trace, RD["timer"])
        yield trace.check(dut.data_out, bv(0x00000001 + i, 32), f"Timer value = 0x0000000{i+1}")
        yield trace.check(dut.pwm, BinaryValue("1"), f" PWM value = 0x00000001")
        yield trace.check(dut.irq, BinaryValue("0"), "IRQ should not be triggered")
    # Step 6: Assert that PWM is Low after 50% of the Top value
    for i in range(8):
        await bus_read(dut, trace, RD["timer"])
        yield trace.check(dut.data_out, bv(0x00000008 + i, 32), f"Timer value = 0x0000000{i+8}")
        yield trace.check(dut.pwm, BinaryValue("0"), f" PWM value = 0x00000000")
        yield trace.check(dut.irq, BinaryValue("0"), "IRQ should not be triggered")
    # Step 7: Assert that it wraps around to 0x00000000
    for i in range(8):
        await bus_read(dut, trace, RD["timer"])
        yield trace.check(dut.data_out, bv(0x00000000 + i, 32), f"Timer value = 0x0000000{i+16}")
        yield trace.check(dut.pwm, BinaryValue("1"), f" PWM value = 0x00000001")
        yield trace.check(dut.irq, BinaryValue("0"), "IRQ should not be triggered")
    
    

# -----------------------------------------------------------------------------
# Synthesis smoke-check
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_TIMER_synthesis():
    TIMER.build_vhd()
    TIMER.build_netlistsvg()

# -----------------------------------------------------------------------------
# Pytest entry point
# -----------------------------------------------------------------------------
@pytest.mark.testcases
def test_timer_hold():
    TIMER.test_with(tb_timer_hold)

@pytest.mark.testcases
def test_timer_wrap():
    TIMER.test_with(tb_timer_wrap)

if __name__ == "__main__":
    lib.run_test(__file__)
