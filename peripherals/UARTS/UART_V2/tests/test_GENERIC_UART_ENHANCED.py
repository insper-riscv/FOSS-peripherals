import pytest
import cocotb
from cocotb.binary import BinaryValue
from cocotb.triggers import Timer
from lib.entity import Entity
import lib
from peripherals.UARTS.UART_V2.tests.test_GENERIC_UART_ENHANCED_package import GENERIC_UART_ENHANCED as GENERIC_UART_ENHANCED_TB

class GENERIC_UART_ENHANCED(Entity):
    """Wrapper for the enhanced generic_uart DUT with FIFO buffers."""
    _package = GENERIC_UART_ENHANCED_TB
    
    # Pins
    clk         = Entity.Input_pin
    reset       = Entity.Input_pin
    data_i      = Entity.Input_pin
    data_o      = Entity.Output_pin
    wr_i        = Entity.Input_pin
    rd_i        = Entity.Input_pin
    operation   = Entity.Input_pin
    rx_i        = Entity.Input_pin
    tx_o        = Entity.Output_pin
    tx_interrupt_o    = Entity.Output_pin
    rx_interrupt_o    = Entity.Output_pin
    error_interrupt_o = Entity.Output_pin

    # Default generics
    DATA_WIDTH             = 32
    UART_DATA_BITS         = 8
    COUNTER_WIDTH          = 16
    FRACTIONAL_WIDTH       = 8
    TX_FIFO_DEPTH          = 16
    RX_FIFO_DEPTH          = 16
    OP_WIDTH               = 3
    CONTROL_SIGNAL_WIDTH   = 4

    # Operation codes
    OP_CONFIG = 0    # Config write/read
    OP_TX_DATA = 1   # TX data write  
    OP_RX_DATA = 2   # RX data read
    OP_STATUS = 3    # Status read
    OP_BAUD = 4      # Baud config (same as config for now)
    OP_FIFO = 5      # FIFO control (same as config for now)

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


@GENERIC_UART_ENHANCED.testcase
async def tb_enhanced_basic_config(dut, trace: lib.Waveform):
    """Test basic enhanced UART configuration."""
    trace.disable()

    # Reset sequence
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()

    # Write a basic config value
    config_value = 0x12345678
    dut.operation.value = GENERIC_UART_ENHANCED.OP_CONFIG
    dut.data_i.value = config_value
    dut.wr_i.value = 1
    await trace.cycle()
    dut.wr_i.value = 0
    await trace.cycle()

    # Read config back
    dut.operation.value = GENERIC_UART_ENHANCED.OP_CONFIG
    dut.rd_i.value = 1
    await trace.cycle()
    
    # Check that we can read back the config
    yield trace.check(
        dut.data_o,
        BinaryValue(value=config_value,
                    n_bits=int(dut.data_o.value.n_bits),
                    bigEndian=False)
    )
    
    dut.rd_i.value = 0


@pytest.mark.synthesis
def test_GENERIC_UART_ENHANCED_synthesis():
    """Test enhanced UART synthesis."""
    GENERIC_UART_ENHANCED.build_vhd()


@pytest.mark.testcases  
def test_GENERIC_UART_ENHANCED_testcases():
    """Run enhanced UART test case."""
    GENERIC_UART_ENHANCED.test_with(tb_enhanced_basic_config) 