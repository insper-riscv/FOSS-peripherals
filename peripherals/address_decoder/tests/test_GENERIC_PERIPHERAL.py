import pytest
from cocotb.binary import BinaryValue
import cocotb

import lib
from test_GENERICS_package import GENERICS

class GENERIC_PERIPHERAL(lib.Entity):
    _package = GENERICS

    clk = lib.Entity.Input_pin
    reset = lib.Entity.Input_pin
    cs = lib.Entity.Input_pin
    data_in = lib.Entity.Input_pin
    data_out = lib.Entity.Output_pin
    ack = lib.Entity.Output_pin

    # Class variables to store parameters for testing
    peripheral_id = 0
    data_width = 32

    @classmethod
    def configure(cls, peripheral_id, data_width=None):
        """Configure the class with generic parameters"""
        cls.peripheral_id = peripheral_id
        if data_width is not None:
            cls.data_width = data_width
        return cls

    @classmethod
    def test_with(cls, testcase):
        """Override test_with to include generics"""
        parameters = {
            "PERIPHERAL_ID": cls.peripheral_id,
            "DATA_WIDTH": cls.data_width,
        }

        # Call parent method with parameters
        super().test_with(testcase, parameters=parameters)
       
@GENERIC_PERIPHERAL.testcase
async def tb_GENERIC_PERIPHERAL_case_1(dut: GENERIC_PERIPHERAL, trace: lib.Waveform):
    """Test the GENERIC_PERIPHERAL invalid input"""

    # Create a clock generator
    clock = cocotb.clock.Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize all inputs
    dut.cs.value = 0
    dut.data_in.value = 0
    dut.reset.value = 0

    # Wait a few cycles to stabilize
    await cocotb.triggers.ClockCycles(dut.clk, 5)

    # Apply reset
    dut.reset.value = 1
    await cocotb.triggers.ClockCycles(dut.clk, 5)

    # Now check outputs during reset - use full width for binary values
    zero32 = BinaryValue(value=0, n_bits=32, bigEndian=False)
    yield trace.check(dut.ack, BinaryValue(value=0, n_bits=1))
    yield trace.check(dut.data_out, zero32)

    # Release reset, keep cs inactive
    dut.reset.value = 0
    await cocotb.triggers.ClockCycles(dut.clk, 5)

    # Check outputs after reset, with cs=0
    yield trace.check(dut.ack, BinaryValue(value=0, n_bits=1))
    yield trace.check(dut.data_out, zero32)

    # Now try with cs=1
    dut.cs.value = 1
    await cocotb.triggers.ClockCycles(dut.clk, 5)

    # Check outputs with cs=1 - explicitly create 32-bit binary value for 42
    id32 = BinaryValue(value=42, n_bits=32, bigEndian=False)
    yield trace.check(dut.ack, BinaryValue(value=1, n_bits=1))
    yield trace.check(dut.data_out, id32)

@GENERIC_PERIPHERAL.testcase
async def tb_GENERIC_PERIPHERAL_case_2(dut: GENERIC_PERIPHERAL, trace: lib.Waveform):
    """Test the GENERIC_PERIPHERAL valid input"""

    # Create a clock generator
    clock = cocotb.clock.Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize all inputs
    dut.cs.value = 0
    dut.data_in.value = 0

    # Start with reset
    dut.reset.value = 1
    await cocotb.triggers.ClockCycles(dut.clk, 3)

    # Create properly sized binary values for comparison
    zero32 = BinaryValue(value=0, n_bits=32, bigEndian=False)
    id32 = BinaryValue(value=42, n_bits=32, bigEndian=False)  # PERIPHERAL_ID = 42

    # Verify reset state
    yield trace.check(dut.ack, BinaryValue(value=0, n_bits=1))
    yield trace.check(dut.data_out, zero32)

    # Release reset
    dut.reset.value = 0
    await cocotb.triggers.ClockCycles(dut.clk, 2)

    # Test with CS active - should activate peripheral
    dut.cs.value = 1
    await cocotb.triggers.ClockCycles(dut.clk, 3)

    # Verify peripheral outputs ID when selected
    yield trace.check(dut.ack, BinaryValue(value=1, n_bits=1))
    yield trace.check(dut.data_out, id32)

    # Test with CS inactive - should deactivate peripheral
    dut.cs.value = 0
    await cocotb.triggers.ClockCycles(dut.clk, 3)

    # Verify peripheral outputs zeros when deselected
    yield trace.check(dut.ack, BinaryValue(value=0, n_bits=1))
    yield trace.check(dut.data_out, zero32)

    # Test rapid toggling of CS
    for _ in range(3):
        # Activate peripheral
        dut.cs.value = 1
        await cocotb.triggers.ClockCycles(dut.clk, 2)

        # Verify activation
        yield trace.check(dut.ack, BinaryValue(value=1, n_bits=1))
        yield trace.check(dut.data_out, id32)

        # Deactivate peripheral
        dut.cs.value = 0
        await cocotb.triggers.ClockCycles(dut.clk, 2)

        # Verify deactivation
        yield trace.check(dut.ack, BinaryValue(value=0, n_bits=1))
        yield trace.check(dut.data_out, zero32)


@pytest.mark.synthesis
def test_GENERIC_PERIPHERAL_synthesis():
    """Test the GENERIC_PERIPHERAL synthesis"""
    GENERIC_PERIPHERAL.build_vhd()

@pytest.mark.testcases
def test_GENERIC_PERIPHERAL_testcases():
    """Test the GENERIC_PERIPHERAL testcases"""
    GENERIC_PERIPHERAL.configure(42)
    GENERIC_PERIPHERAL.test_with(tb_GENERIC_PERIPHERAL_case_1)
    GENERIC_PERIPHERAL.test_with(tb_GENERIC_PERIPHERAL_case_2)

if __name__ == "__main__":
    lib.run_tests(__file__)