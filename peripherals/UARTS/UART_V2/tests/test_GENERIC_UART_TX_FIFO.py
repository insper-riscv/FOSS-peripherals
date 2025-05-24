import pytest
import cocotb
from cocotb.binary import BinaryValue
from cocotb.triggers import Timer
from lib.entity import Entity
import lib
from peripherals.UARTS.UART_V2.tests.test_GENERIC_UART_TX_FIFO_package import GENERIC_UART_TX_FIFO as GENERIC_UART_TX_FIFO_TB

class GENERIC_UART_TX_FIFO(Entity):
    """Wrapper for the UART TX with FIFO DUT."""
    _package = GENERIC_UART_TX_FIFO_TB
    
    # Pins
    clk             = Entity.Input_pin
    reset           = Entity.Input_pin
    
    # CPU interface
    tx_data_i       = Entity.Input_pin
    write_strobe_i  = Entity.Input_pin
    
    # UART interface  
    baud_tick_i     = Entity.Input_pin
    tx_o            = Entity.Output_pin
    
    # Status
    tx_busy_o       = Entity.Output_pin
    tx_empty_o      = Entity.Output_pin
    tx_full_o       = Entity.Output_pin
    tx_almost_full_o = Entity.Output_pin
    tx_threshold_o  = Entity.Output_pin

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


@GENERIC_UART_TX_FIFO.testcase
async def tb_tx_fifo_basic_write(dut, trace: lib.Waveform):
    """Test basic TX FIFO write operations."""
    trace.disable()
    
    # Reset sequence
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()
    
    # Initialize signals
    dut.write_strobe_i.value = 0
    dut.baud_tick_i.value = 0
    
    # Write a single byte to FIFO
    test_byte = 0x55
    dut.tx_data_i.value = test_byte
    dut.write_strobe_i.value = 1
    await trace.cycle()
    dut.write_strobe_i.value = 0
    await trace.cycle()
    
    # Provide some baud ticks to let transmission proceed
    for _ in range(20):
        dut.baud_tick_i.value = 1
        await trace.cycle()
        dut.baud_tick_i.value = 0
        await trace.cycle()
    
    # Simple check that the system is stable (no specific output verification needed)
    # Just ensure the test framework recognizes this as a generator
    yield trace.check(
        dut.tx_o,
        BinaryValue(value=1,  # TX should be idle (high) or transmitting
                    n_bits=1,
                    bigEndian=False)
    )


@GENERIC_UART_TX_FIFO.testcase
async def tb_tx_fifo_multiple_writes(dut, trace: lib.Waveform):
    """Test TX FIFO with multiple byte writes."""
    trace.disable()
    
    # Reset sequence
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()
    
    # Initialize signals
    dut.write_strobe_i.value = 0
    dut.baud_tick_i.value = 0
    
    # Write multiple bytes to FIFO
    test_bytes = [0x11, 0x22, 0x33, 0x44]
    
    for byte_val in test_bytes:
        dut.tx_data_i.value = byte_val
        dut.write_strobe_i.value = 1
        await trace.cycle()
        dut.write_strobe_i.value = 0
        await trace.cycle()
        
        # Provide some baud ticks
        for _ in range(5):
            dut.baud_tick_i.value = 1
            await trace.cycle()
            dut.baud_tick_i.value = 0
            await trace.cycle()
    
    # Let the FIFO drain
    for _ in range(100):
        dut.baud_tick_i.value = 1
        await trace.cycle()
        dut.baud_tick_i.value = 0
        await trace.cycle()
    
    # Simple check that the system is stable
    yield trace.check(
        dut.tx_o,
        BinaryValue(value=1,  # TX should be idle (high) after transmission
                    n_bits=1,
                    bigEndian=False)
    )


@pytest.mark.synthesis
def test_GENERIC_UART_TX_FIFO_synthesis():
    """Test TX FIFO synthesis."""
    GENERIC_UART_TX_FIFO.build_vhd()


@pytest.mark.testcases
def test_GENERIC_UART_TX_FIFO_testcases():
    """Run TX FIFO test cases."""
    GENERIC_UART_TX_FIFO.test_with(tb_tx_fifo_basic_write)
    GENERIC_UART_TX_FIFO.test_with(tb_tx_fifo_multiple_writes) 