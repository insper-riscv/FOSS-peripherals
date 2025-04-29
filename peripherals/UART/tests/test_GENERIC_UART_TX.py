import pytest
from cocotb.binary import BinaryValue
from lib.entity import Entity
import lib
from test_TYPES_package import TYPES

class GENERIC_UART_TX(Entity):
    """Wrapper for the Generic UART TX with individual generic parameters"""

    _package = TYPES

    # Define pins
    clk = Entity.Input_pin
    reset = Entity.Input_pin
    tx_data_i = Entity.Input_pin
    write_strobe_i = Entity.Input_pin
    baud_tick_i = Entity.Input_pin
    tx_o = Entity.Output_pin
    tx_ready_o = Entity.Output_pin

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

@GENERIC_UART_TX.testcase
async def tb_uart_tx_single_byte(dut, trace: lib.Waveform):
    """
    Test that a single byte is transmitted correctly, including start, data,
    parity, and stop bits. Each bit is checked on tx_o immediately after
    de‑asserting baud_tick_i, then we wait one cycle before the next bit.
    """
    trace.disable()

    # reset
    dut.reset.value       = 1
    dut.baud_tick_i.value = 0
    dut.write_strobe_i.value = 0
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()

    # idle = '1'
    yield trace.check(dut.tx_o, BinaryValue(1))

    # drive data + strobe
    DATA_BITS = int(dut.tx_data_i.value.n_bits)
    test_data = 0xA5 & ((1 << DATA_BITS) - 1)
    dut.tx_data_i.value      = test_data
    dut.write_strobe_i.value = 1
    await trace.cycle()
    dut.write_strobe_i.value = 0

    # align into START state
    await trace.cycle()

    # build expected: start, data LSB‑first, parity, stop
    parity   = 0
    expected = [0] + [(test_data >> i) & 1 for i in range(DATA_BITS)] + [0] + [1]
    for i in range(DATA_BITS):
        parity ^= (test_data >> i) & 1
    expected[-2] = parity

    # now clock out each bit
    for exp_bit in expected:
        # assert baud tick for one clk cycle
        dut.baud_tick_i.value = 1
        await trace.cycle()
        dut.baud_tick_i.value = 0
        await trace.cycle()
        print(f"Expected: {exp_bit}, Actual: {dut.tx_o.value}")
        # sample after baud tick has been processed
        yield trace.check(dut.tx_o, BinaryValue(str(exp_bit)))

    # finally, tx_ready_o should go high one cycle after STOP
    await trace.cycle()
    yield trace.check(dut.tx_ready_o, BinaryValue(1))

@GENERIC_UART_TX.testcase
async def tb_uart_tx_idle_line(dut, trace: lib.Waveform):
    """
    Test that tx_o is high when idle and tx_ready_o is high.
    This ensures the transmitter is ready and the line is idle after reset.
    """
    trace.disable()
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()
    # After reset, the UART TX line should be idle (high)
    yield trace.check(dut.tx_o, BinaryValue(1))
    # The transmitter should be ready to accept new data
    yield trace.check(dut.tx_ready_o, BinaryValue(1))

@GENERIC_UART_TX.testcase
async def tb_uart_tx_ready_signal(dut, trace: lib.Waveform):
    """
    Test that tx_ready_o goes low during transfer and high after.
    This checks the ready signal is deasserted while transmitting and asserted after.
    """
    trace.disable()
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()
    DATA_BITS = int(dut.tx_data_i.value.n_bits)
    test_data = 0x55 & ((1 << DATA_BITS) - 1)
    dut.tx_data_i.value = test_data
    dut.write_strobe_i.value = 1
    await trace.cycle()
    dut.write_strobe_i.value = 0
    await trace.cycle()
    yield trace.check(dut.tx_ready_o, BinaryValue(str(0)))
    
    total_bits = 1 + DATA_BITS + 1 + 1
    for _ in range(total_bits):
        # Simulate baud ticks for the entire frame (start, data, parity, stop)
        dut.baud_tick_i.value = 1
        await trace.cycle()
        dut.baud_tick_i.value = 0
        await trace.cycle()
    # After the stop bit, tx_ready_o should return high (ready)
    yield trace.check(dut.tx_ready_o, BinaryValue(1))

@pytest.mark.synthesis
def test_GENERIC_UART_TX_synthesis():
    """Test the GENERIC_UART_TX synthesis"""
    GENERIC_UART_TX.build_vhd()

@pytest.mark.testcases
def test_GENERIC_UART_TX_testcases():
    """Run testcases for GENERIC_UART_TX with different parameters"""
    uart = GENERIC_UART_TX.configure(data_bits=8)
    uart.test_with(tb_uart_tx_single_byte)
    uart.test_with(tb_uart_tx_idle_line)
    uart.test_with(tb_uart_tx_ready_signal)

if __name__ == "__main__":
    lib.run_tests(__file__)