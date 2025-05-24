import pytest
import cocotb
from cocotb.binary import BinaryValue
from cocotb.triggers import Timer
from lib.entity import Entity
import lib
from peripherals.UARTS.UART_V2.tests.test_GENERIC_FIFO_package import GENERIC_FIFO as GENERIC_FIFO_TB

class GENERIC_FIFO(Entity):
    """Wrapper for the generic_fifo DUT."""
    _package = GENERIC_FIFO_TB
    
    # Pins
    clk         = Entity.Input_pin
    reset       = Entity.Input_pin
    wr_en       = Entity.Input_pin
    wr_data     = Entity.Input_pin
    rd_en       = Entity.Input_pin
    rd_data     = Entity.Output_pin
    empty       = Entity.Output_pin
    full        = Entity.Output_pin
    almost_empty = Entity.Output_pin
    almost_full = Entity.Output_pin
    count       = Entity.Output_pin

    # Default generics
    DATA_WIDTH = 8
    FIFO_DEPTH = 16

    @classmethod
    def configure(cls, data_width=None, fifo_depth=None):
        """Override any of the numeric generics if desired."""
        if data_width is not None: 
            cls.DATA_WIDTH = data_width
        if fifo_depth is not None: 
            cls.FIFO_DEPTH = fifo_depth
        return cls

    @classmethod
    def test_with(cls, testcase, parameters=None):
        """Provide generics to the DUT."""
        super().test_with(testcase, parameters=parameters)


@GENERIC_FIFO.testcase
async def tb_fifo_basic_test(dut, trace: lib.Waveform):
    """Test basic FIFO operations following UART pattern."""
    trace.disable()
    
    # Reset sequence (same as UART)
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()
    
    # Write a single byte and read it back
    test_value = 0xA5
    dut.wr_en.value = 1
    dut.wr_data.value = test_value
    await trace.cycle()
    
    # Deassert write
    dut.wr_en.value = 0
    await trace.cycle()
    
    # Check that we can read the value back
    yield trace.check(
        dut.rd_data,
        BinaryValue(value=test_value,
                    n_bits=int(dut.rd_data.value.n_bits),
                    bigEndian=False)
    )


@GENERIC_FIFO.testcase
async def tb_fifo_multiple_values(dut, trace: lib.Waveform):
    """Test FIFO with multiple values."""
    trace.disable()
    
    # Reset sequence
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()
    
    # Write multiple values
    test_values = [0x11, 0x22, 0x33, 0x44]
    
    for value in test_values:
        dut.wr_en.value = 1
        dut.wr_data.value = value
        await trace.cycle()
        dut.wr_en.value = 0
        await trace.cycle()
    
    # Read values back in FIFO order
    for expected_value in test_values:
        yield trace.check(
            dut.rd_data,
            BinaryValue(value=expected_value,
                        n_bits=int(dut.rd_data.value.n_bits),
                        bigEndian=False)
        )
        
        # Advance the read pointer
        dut.rd_en.value = 1
        await trace.cycle()
        dut.rd_en.value = 0
        await trace.cycle()


@GENERIC_FIFO.testcase
async def tb_fifo_simultaneous_read_write(dut, trace: lib.Waveform):
    """Test simultaneous read and write operations."""
    trace.disable()
    
    # Reset sequence
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()
    
    # Write initial data
    dut.wr_en.value = 1
    dut.wr_data.value = 0x55
    await trace.cycle()
    dut.wr_en.value = 0
    await trace.cycle()
    
    # Verify we can read it
    yield trace.check(
        dut.rd_data,
        BinaryValue(value=0x55,
                    n_bits=int(dut.rd_data.value.n_bits),
                    bigEndian=False)
    )
    
    # Simultaneous read old value and write new value
    dut.rd_en.value = 1
    dut.wr_en.value = 1
    dut.wr_data.value = 0xAA
    await trace.cycle()
    dut.rd_en.value = 0
    dut.wr_en.value = 0
    await trace.cycle()
    
    # Should now have the new value available
    yield trace.check(
        dut.rd_data,
        BinaryValue(value=0xAA,
                    n_bits=int(dut.rd_data.value.n_bits),
                    bigEndian=False)
    )


@pytest.mark.synthesis
def test_GENERIC_FIFO_synthesis():
    """Test FIFO synthesis."""
    GENERIC_FIFO.build_vhd()


@pytest.mark.testcases
def test_GENERIC_FIFO_testcases():
    """Run FIFO test cases."""
    GENERIC_FIFO.test_with(tb_fifo_basic_test)
    GENERIC_FIFO.test_with(tb_fifo_multiple_values)
    GENERIC_FIFO.test_with(tb_fifo_simultaneous_read_write) 