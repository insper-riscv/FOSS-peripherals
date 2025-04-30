import pytest
from cocotb.binary import BinaryValue
from lib.entity import Entity
import lib
from test_TYPES_package import TYPES

class GENERIC_UART_RX(Entity):
    """Wrapper for the Generic UART RX with individual generic parameters"""

    _package = TYPES

    # Define pins
    clk = Entity.Input_pin
    reset = Entity.Input_pin
    rx_i = Entity.Input_pin
    baud_tick_i = Entity.Input_pin
    rx_data_o = Entity.Output_pin
    rx_ready_o = Entity.Output_pin
    read_strobe_i = Entity.Input_pin
    parity_error_o = Entity.Output_pin

    # Default generics
    DATA_BITS = 8

    @classmethod
    def configure(cls, data_bits=8):
        cls.DATA_BITS = data_bits
        return cls

    @classmethod
    def test_with(cls, testcase, parameters=None):
        if parameters is None:
            parameters = {
                "DATA_BITS": cls.DATA_BITS
            }
        super().test_with(testcase, parameters=parameters)

@GENERIC_UART_RX.testcase
async def tb_uart_rx_single_byte(dut, trace: lib.Waveform):
    """
    Send a valid byte frame (start, data LSB-first, parity, stop)
    and check the received data and ready signal.
    """
    trace.disable()
    # reset
    dut.reset.value = 1
    dut.baud_tick_i.value = 0
    dut.rx_i.value = 1
    dut.read_strobe_i.value = 0
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()

    # drive frame
    DATA_BITS = dut.DATA_BITS.value.integer
    test_data = 0xA5 & ((1 << DATA_BITS) - 1)
    # compute parity (even)
    parity = 0
    for i in range(DATA_BITS):
        parity ^= (test_data >> i) & 1

    frame = [0, 0] \
        + [(test_data >> i) & 1 for i in range(DATA_BITS)] \
        + [parity] \
        + [1]
    
    # send each bit on baud tick
    for bit in frame:
        dut.rx_i.value = bit
        dut.baud_tick_i.value = 1
        await trace.cycle()
        dut.baud_tick_i.value = 0
        await trace.cycle()

    data_str = f"{test_data:0{DATA_BITS}b}"

    # after STOP, data should be ready
    yield trace.check(dut.rx_data_o, BinaryValue(data_str))
    yield trace.check(dut.rx_ready_o, BinaryValue(1))
    # parity_error_o should be low
    yield trace.check(dut.parity_error_o, BinaryValue(str(0)))

@GENERIC_UART_RX.testcase
async def tb_uart_rx_idle(dut, trace: lib.Waveform):
    """
    With idle line (rx_i high), rx_ready_o stays low and no data appears.
    """
    trace.disable()
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    dut.rx_i.value = 1
    await trace.cycle()
    # no start bit seen
    yield trace.check(dut.rx_ready_o, BinaryValue(str(0)))

@GENERIC_UART_RX.testcase
async def tb_uart_rx_parity_error(dut, trace: lib.Waveform):
    """
    Send a frame with incorrect parity and check parity_error_o goes high.
    """
    trace.disable()
    # reset
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()

    DATA_BITS = dut.DATA_BITS.value.integer
    test_data = 0x3C & ((1 << DATA_BITS) - 1)
    # compute correct parity and flip it
    parity = 0
    for i in range(DATA_BITS):
        parity ^= (test_data >> i) & 1
    bad_parity = parity ^ 1

    frame = [0, 0] \
        + [(test_data >> i) & 1 for i in range(DATA_BITS)] \
        + [bad_parity] \
        + [1]
    for bit in frame:
        dut.rx_i.value = bit
        dut.baud_tick_i.value = 1
        await trace.cycle()
        dut.baud_tick_i.value = 0
        await trace.cycle()

    # parity_error_o should be asserted, rx_ready_o still goes high after stop
    yield trace.check(dut.parity_error_o, BinaryValue(1))
    yield trace.check(dut.rx_ready_o, BinaryValue(1))

@GENERIC_UART_RX.testcase
async def tb_uart_rx_read_strobe(dut, trace: lib.Waveform):
    """
    After a valid reception, asserting read_strobe_i should clear rx_ready_o.
    """
    trace.disable()
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()

    # send one good byte (0x5A)
    DATA_BITS = dut.DATA_BITS.value.integer
    test_data = 0x5A & ((1 << DATA_BITS) - 1)
    parity = 0
    for i in range(DATA_BITS):
        parity ^= (test_data >> i) & 1
    frame = [0, 0] + [(test_data >> i) & 1 for i in range(DATA_BITS)] + [parity] + [1]
    for bit in frame:
        dut.rx_i.value = bit
        dut.baud_tick_i.value = 1
        await trace.cycle()
        dut.baud_tick_i.value = 0
        await trace.cycle()

    # now rx_ready_o should be high
    yield trace.check(dut.rx_ready_o, BinaryValue(1))
    # assert read strobe
    dut.read_strobe_i.value = 1
    await trace.cycle()
    # rx_ready_o should go low
    yield trace.check(dut.rx_ready_o, BinaryValue(str(0)))

@pytest.mark.synthesis
def test_GENERIC_UART_RX_synthesis():
    """Test the GENERIC_UART_RX synthesis"""
    GENERIC_UART_RX.build_vhd()

@pytest.mark.testcases
def test_GENERIC_UART_RX_testcases():
    """Run testcases for GENERIC_UART_RX with different parameters"""
    uart = GENERIC_UART_RX.configure(data_bits=8)
    uart.test_with(tb_uart_rx_single_byte)
    uart.test_with(tb_uart_rx_idle)
    uart.test_with(tb_uart_rx_parity_error)
    uart.test_with(tb_uart_rx_read_strobe)

if __name__ == "__main__":
    lib.run_tests(__file__)