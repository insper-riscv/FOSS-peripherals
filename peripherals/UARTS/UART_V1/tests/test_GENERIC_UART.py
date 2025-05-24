import pytest
import cocotb
from cocotb.binary import BinaryValue
from cocotb.triggers import Timer
from lib.entity import Entity
import lib
from peripherals.UARTS.UART_V1.tests.test_GENERIC_UART_package import GENERIC_UART as GENERIC_UART_TB

class GENERIC_UART(Entity):
    """Wrapper for the generic_uart DUT with all sub‐entities/package dependencies."""
    _package = GENERIC_UART_TB

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
    interrupt_o = Entity.Output_pin

    # Default generics (match your VHDL defaults)
    DATA_WIDTH                     = 32
    UART_DATA_BITS                 = 8
    COUNTER_WIDTH                  = 16
    OP_WIDTH                       = 2
    CONTROL_SIGNAL_WIDTH           = 3
    OPERATION_CONTROL_SIGNAL_COUNT = 3

    # “op→ctrl” map defaults from your VHDL generic
    OP_0, OP_1, OP_2 = 0, 1, 2
    CTRL_0, CTRL_1, CTRL_2 = 1, 2, 4
    DEFAULT_CTRL = 0

    @classmethod
    def configure(cls,
                  data_width=None,
                  uart_data_bits=None,
                  counter_width=None,
                  op_width=None,
                  ctrl_width=None,
                  map_count=None):
        """Override any of the numeric generics if desired."""
        if data_width        is not None: cls.DATA_WIDTH                     = data_width
        if uart_data_bits    is not None: cls.UART_DATA_BITS                 = uart_data_bits
        if counter_width     is not None: cls.COUNTER_WIDTH                  = counter_width
        if op_width          is not None: cls.OP_WIDTH                       = op_width
        if ctrl_width        is not None: cls.CONTROL_SIGNAL_WIDTH           = ctrl_width
        if map_count         is not None: cls.OPERATION_CONTROL_SIGNAL_COUNT = map_count
        return cls

    @classmethod
    def test_with(cls, testcase, parameters=None):
        """
        Provide generics to the DUT; by default we let it pick up
        the VHDL defaults, so we only call super() without parameters.
        """
        super().test_with(testcase, parameters=parameters)


@GENERIC_UART.testcase
async def tb_config_write_read(dut, trace: lib.Waveform):
    """
    Write a known pattern into the config register (op=OP_0)
    then read it back (rd_i with same op).
    """
    trace.disable()

    # reset sequence
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()

    # Write CONFIG = 0x_A5_A5_A5_A5
    pattern = 0xA5A5A5A5
    dut.operation.value = GENERIC_UART.OP_0
    dut.data_i.value   = pattern
    dut.wr_i.value     = 1
    await trace.cycle()

    # deassert write
    dut.wr_i.value = 0
    await trace.cycle()

    # now READ it back
    dut.operation.value = GENERIC_UART.OP_0
    dut.rd_i.value      = 1
    await trace.cycle()

    # check data_o == pattern
    yield trace.check(
        dut.data_o,
        BinaryValue(value=pattern,
                    n_bits=int(dut.data_o.value.n_bits),
                    bigEndian=False)
    )

@GENERIC_UART.testcase
async def tb_tx_data_path(dut, trace: lib.Waveform):
    """
    Send one byte over the TX path:
      1) enable TX (via config register)
      2) write one data byte with op=OP_1
      3) wait for tx_ready_o → 1
      4) check for interrupt_o -> 1 as tx_ready_o was triggered
    """
    trace.disable()
    # reset
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()

    # enable TX only (set bit COUNTER_WIDTH+1 in config)
    cfg = 1 << (GENERIC_UART.COUNTER_WIDTH + 1)
    dut.operation.value = GENERIC_UART.OP_0
    dut.data_i.value   = cfg
    dut.wr_i.value     = 1
    await trace.cycle()
    dut.wr_i.value = 0
    await trace.cycle()

    # write a byte (e.g. 0x5A) to TX register
    tx_byte = 0x5A
    dut.operation.value = GENERIC_UART.OP_1
    dut.data_i.value   = tx_byte
    dut.wr_i.value     = 1
    await trace.cycle()
    dut.wr_i.value = 0

    # wait for interrupt → indicates TX is done (tx_ready & en_tx)
    for _ in range(100):
        await trace.cycle()
        if int(dut.interrupt_o.value) == 1:
            break
    yield trace.check(dut.interrupt_o, BinaryValue(1))


@GENERIC_UART.testcase
async def tb_rx_data_path(dut, trace: lib.Waveform):
    """
    Feed one byte into the RX path:
      1) enable RX
      2) bit-bang start + 8 data bits + stop
      3) wait for rx_ready_o
      4) read back via op=OP_2
    """
    

    trace.disable()
    # reset
    dut.reset.value = 1
    await trace.cycle()
    dut.reset.value = 0
    await trace.cycle()

    # enable RX only (set bit COUNTER_WIDTH in config)
    cfg = 1 << GENERIC_UART.COUNTER_WIDTH
    dut.operation.value = GENERIC_UART.OP_0
    dut.data_i.value   = cfg
    dut.wr_i.value     = 1
    await trace.cycle()
    dut.wr_i.value = 0
    await trace.cycle()

    # now bit-bang a single byte, LSB first, no parity, 1 stop bit
    #------------------------------------------------------------------
    # drive the line IDLE (mark) = '1' for one full bit period
    dut.rx_i.value = 1
    await trace.cycle()

    rx_byte = 0xA3
    # start bit (0)
    dut.rx_i.value = 0
    await trace.cycle() # tick #1: move IDLE→START
    await trace.cycle() # tick #2: START sees '0', moves to DATA
    # data bits
    for i in range(8):
        dut.rx_i.value = (rx_byte >> i) & 1
        await trace.cycle()
    # stop bit (1)
    dut.rx_i.value = 1
    await trace.cycle()

    # give the RX‐register a cycle to latch before we read it back
    await trace.cycle()

    # wait for interrupt → indicates RX is done (rx_ready & en_rx)
    for _ in range(100):
        await trace.cycle()
        if int(dut.interrupt_o.value) == 1:
            break
    yield trace.check(dut.interrupt_o, BinaryValue(1))

    await trace.cycle()
    
    # now read the received byte out using op=OP_2
    dut.operation.value = GENERIC_UART.OP_2
    dut.rd_i.value      = 1
    await trace.cycle()
    print(f"rx_byte: {rx_byte}")
    print(f"data_o: {dut.data_o.value.integer}")
    yield trace.check(
        dut.data_o,
        BinaryValue(value=rx_byte,
                    n_bits=int(dut.data_o.value.n_bits),
                    bigEndian=False)
    )

@GENERIC_UART.testcase
async def tb_interrupt_clearing(dut, trace: lib.Waveform):
    """
    After a RX event and then a readback, interrupt_o should clear.
    """
    trace.disable()
    # assume RX test already passed → interrupt_o == 1
    # now perform the OP_2 read to clear the pending RX interrupt
    dut.operation.value = GENERIC_UART.OP_2
    dut.rd_i.value      = 1
    await trace.cycle()
    dut.rd_i.value = 0
    await trace.cycle()
    # interrupt must now be low
    yield trace.check(dut.interrupt_o, BinaryValue(0, n_bits=1))

@pytest.mark.synthesis
def test_GENERIC_UART_synthesis():
    """Just ensure we can elaborate/build the generic_uart VHDL."""
    GENERIC_UART.build_vhd()


@pytest.mark.testcases
def test_GENERIC_UART_testcases():
    """Hook our cocotb test(s) into pytest."""
    GENERIC_UART.test_with(tb_config_write_read)
    GENERIC_UART.test_with(tb_tx_data_path)
    GENERIC_UART.test_with(tb_rx_data_path)
    GENERIC_UART.test_with(tb_interrupt_clearing)


if __name__ == "__main__":
    lib.run_tests(__file__)