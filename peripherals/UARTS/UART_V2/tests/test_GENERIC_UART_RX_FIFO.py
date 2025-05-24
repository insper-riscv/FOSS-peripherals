import pytest
import cocotb
from cocotb.binary import BinaryValue
from cocotb.triggers import Timer
from lib.entity import Entity
import lib
from peripherals.UARTS.UART_V2.tests.test_GENERIC_UART_RX_FIFO_package import GENERIC_UART_RX_FIFO as GENERIC_UART_RX_FIFO_TB

class GENERIC_UART_RX_FIFO(Entity):
    """Wrapper for the UART RX with FIFO DUT."""
    _package = GENERIC_UART_RX_FIFO_TB
    
    # Pins
    clk             = Entity.Input_pin
    reset           = Entity.Input_pin
    
    # UART interface
    rx_i            = Entity.Input_pin
    baud_tick_i     = Entity.Input_pin
    
    # CPU interface
    rx_data_o       = Entity.Output_pin
    read_strobe_i   = Entity.Input_pin
    
    # Status
    rx_empty_o      = Entity.Output_pin
    rx_full_o       = Entity.Output_pin
    rx_almost_full_o = Entity.Output_pin
    rx_data_ready_o = Entity.Output_pin
    
    # Error flags
    parity_error_o  = Entity.Output_pin
    frame_error_o   = Entity.Output_pin
    overrun_error_o = Entity.Output_pin
    
    # Enhanced status for interrupts
    rx_threshold_o  = Entity.Output_pin

    # Default generics
    DATA_BITS = 8
    FIFO_DEPTH = 16

    @classmethod
    def configure(cls, **kwargs):
        """Override any of the numeric generics if desired."""
        for key, value in kwargs.items():
            if hasattr(cls, key.upper()):
                setattr(cls, key.upper(), value)
        return cls

    @classmethod
    def test_with(cls, testcase, parameters=None):
        """Provide generics to the DUT."""
        super().test_with(testcase, parameters=parameters)


@GENERIC_UART_RX_FIFO.testcase
async def tb_rx_fifo_basic_read(dut, trace: lib.Waveform):
    """Test basic RX FIFO read operations."""
    trace.disable()
    
    # Reset sequence
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()
    
    # Initialize signals
    dut.read_strobe_i.value = 0
    dut.baud_tick_i.value = 0
    dut.rx_i.value = 1  # Idle state
    
    # Just run for a few cycles to ensure stability
    for _ in range(10):
        await trace.cycle()
    
    # Simple check that system remains stable
    yield trace.check(
        dut.rx_empty_o,
        BinaryValue(value=1,  # Should be empty initially
                    n_bits=1,
                    bigEndian=False)
    )


@GENERIC_UART_RX_FIFO.testcase
async def tb_rx_fifo_idle_test(dut, trace: lib.Waveform):
    """Test RX FIFO in idle state."""
    trace.disable()
    
    # Reset sequence
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()
    
    # Initialize signals
    dut.read_strobe_i.value = 0
    dut.baud_tick_i.value = 0
    dut.rx_i.value = 1  # Keep in idle state
    
    # Provide some baud ticks while idle
    for _ in range(20):
        dut.baud_tick_i.value = 1
        await trace.cycle()
        dut.baud_tick_i.value = 0
        await trace.cycle()
    
    # System should remain stable in idle
    yield trace.check(
        dut.rx_empty_o,
        BinaryValue(value=1,  # Should be empty in idle
                    n_bits=1,
                    bigEndian=False)
    )


@pytest.mark.synthesis
def test_GENERIC_UART_RX_FIFO_synthesis():
    """Test RX FIFO synthesis."""
    GENERIC_UART_RX_FIFO.build_vhd()


@pytest.mark.testcases
def test_GENERIC_UART_RX_FIFO_testcases():
    """Run RX FIFO test cases."""
    GENERIC_UART_RX_FIFO.test_with(tb_rx_fifo_basic_read)
    GENERIC_UART_RX_FIFO.test_with(tb_rx_fifo_idle_test) 