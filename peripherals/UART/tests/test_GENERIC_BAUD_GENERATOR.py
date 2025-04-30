import pytest
import random
from cocotb.binary import BinaryValue
from lib.entity import Entity
import lib
from test_TYPES_package import TYPES

class GENERIC_BAUD_GENERATOR(Entity):
    """Wrapper for the GENERIC_BAUD_GENERATOR with individual generic parameters"""

    _package = TYPES

    # Define pins
    clk        = Entity.Input_pin
    reset      = Entity.Input_pin
    baud_div_i = Entity.Input_pin
    tick       = Entity.Output_pin

    # Default generics
    COUNTER_WIDTH = 16

    @classmethod
    def configure(cls, counter_width=16):
        cls.COUNTER_WIDTH = counter_width
        return cls

    @classmethod
    def test_with(cls, testcase, parameters=None):
        if parameters is None:
            parameters = {
                "COUNTER_WIDTH": cls.COUNTER_WIDTH
            }
        super().test_with(testcase, parameters=parameters)

@GENERIC_BAUD_GENERATOR.testcase
async def tb_reset_holds_tick_low(dut, trace: lib.Waveform):
    """While reset is asserted, tick must stay '0'"""
    trace.disable()
    dut.reset.value = 1
    dut.baud_div_i.value = 0
    for _ in range(5):
        await trace.cycle()
        yield trace.check(dut.tick, BinaryValue('0'))
    # release reset, one cycle to propagate
    dut.reset.value = 0
    await trace.cycle()
    # now with div=0 we expect a tick
    yield trace.check(dut.tick, BinaryValue('1'))

@GENERIC_BAUD_GENERATOR.testcase
async def tb_div_by_zero_generates_tick_every_cycle(dut, trace: lib.Waveform):
    """With baud_div_i = 0, tick should go high every clock"""
    trace.disable()
    dut.reset.value = 0
    dut.baud_div_i.value = 0
    for _ in range(4):
        await trace.cycle()
        yield trace.check(dut.tick, BinaryValue('1'))

@GENERIC_BAUD_GENERATOR.testcase
async def tb_div_by_n_generates_periodic_tick(dut, trace: lib.Waveform):
    """With baud_div_i = N, tick should pulse once every N+1 cycles"""
    trace.disable()
    dut.reset.value = 0
    N = 3
    dut.baud_div_i.value = N
    # First N clocks no tick, then 1 tick
    for cycle in range(8):
        await trace.cycle()
        expected = '1' if ((cycle % (N+1)) == N) else '0'
        yield trace.check(dut.tick, BinaryValue(expected))

@GENERIC_BAUD_GENERATOR.testcase
async def tb_random_divisors(dut, trace: lib.Waveform):
    """Test a few random divisors within counter range"""
    trace.disable()
    dut.reset.value = 0
    width = dut.COUNTER_WIDTH.value.integer
    for _ in range(5):
        div = random.randint(0, (1 << width)-1)
        dut.baud_div_i.value = div
        # cycle through one full period
        for cycle in range(div+1):
            await trace.cycle()
            expected = '1' if cycle==div else '0'
            yield trace.check(dut.tick, BinaryValue(expected))

@pytest.mark.synthesis
def test_GENERIC_BAUD_GENERATOR_synthesis():
    """Test the GENERIC_BAUD_GENERATOR synthesis"""
    GENERIC_BAUD_GENERATOR.build_vhd()

@pytest.mark.testcases
def test_GENERIC_BAUD_GENERATOR_testcases():
    """Run all GENERIC_BAUD_GENERATOR testcases"""
    bg = GENERIC_BAUD_GENERATOR.configure(counter_width=16)
    bg.test_with(tb_reset_holds_tick_low)
    bg.test_with(tb_div_by_zero_generates_tick_every_cycle)
    bg.test_with(tb_div_by_n_generates_periodic_tick)
    bg.test_with(tb_random_divisors)

if __name__ == "__main__":
    lib.run_tests(__file__)