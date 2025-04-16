import cocotb
from cocotb.triggers import RisingEdge
from cocotb.binary import BinaryValue
import random
import pytest
import lib


class TIMER_OPERATION_DECODER(lib.Entity):
    """
    Class representing the TIMER_OPERATION_DECODER module.
    """
    address = lib.Entity.Input_pin
    write = lib.Entity.Input_pin
    start_counter = lib.Entity.Output_pin
    op_counter = lib.Entity.Output_pin
    load_reset_value = lib.Entity.Output_pin
    read_op = lib.Entity.Output_pin


# Basic Functional Test
@TIMER_OPERATION_DECODER.testcase
async def tb_TIMER_OPERATION_DECODER_case_1(dut: TIMER_OPERATION_DECODER, trace: lib.Waveform):
    """
    Basic test for TIMER_OPERATION_DECODER verifying outputs for known addresses.
    """
    test_vectors = [
        # address, write, expected_start, expected_reset, expected_op, expected_read
        ("0000", '1', '1', '0', "00", '0'),  # Start
        ("0001", '1', '0', '1', "00", '0'),  # Load Reset Value
        ("0010", '0', '0', '0', "01", '0'),  # Load
        ("0011", '0', '0', '0', "10", '0'),  # Reset
        ("0100", '0', '0', '0', "00", '1'),  # Read Overflow
        ("0101", '0', '0', '0', "00", '0'),  # Read Default
        ("1111", '1', '0', '0', "00", '0'),  # No-op
    ]

    for i, (addr, wr, start, reset, op, read) in enumerate(test_vectors, start=1):
        dut.address.value = BinaryValue(addr)
        dut.write.value = int(wr)  # ← correção aqui
        await trace.cycle()

        yield trace.check(dut.start_counter, start, f"Test #{i}: address={addr}, write={wr}")
        yield trace.check(dut.load_reset_value, reset, f"Test #{i}: address={addr}, write={wr}")
        yield trace.check(dut.op_counter, op, f"Test #{i}: address={addr}")
        yield trace.check(dut.read_op, read, f"Test #{i}: address={addr}")


# Randomized Stress Test
@TIMER_OPERATION_DECODER.testcase
async def tb_TIMER_OPERATION_DECODER_random(dut: TIMER_OPERATION_DECODER, trace: lib.Waveform):
    """
    Random test for TIMER_OPERATION_DECODER using random address and write combinations.
    """
    trace.disable()

    for i in range(100):
        addr_int = random.randint(0, 15)
        addr = format(addr_int, '04b')
        wr = random.choice(['0', '1'])

        dut.address.value = BinaryValue(addr)
        dut.write.value = int(wr)  # ← correção aqui
        await trace.cycle()

        expected_start = '1' if addr == "0000" and wr == '1' else '0'
        expected_reset = '1' if addr == "0001" and wr == '1' else '0'
        expected_op = "01" if addr == "0010" else "10" if addr == "0011" else "00"
        expected_read = '1' if addr == "0100" else '0'

        yield trace.check(dut.start_counter, expected_start, f"[Rand #{i}] addr={addr}, write={wr}")
        yield trace.check(dut.load_reset_value, expected_reset, f"[Rand #{i}] addr={addr}, write={wr}")
        yield trace.check(dut.op_counter, expected_op, f"[Rand #{i}] addr={addr}")
        yield trace.check(dut.read_op, expected_read, f"[Rand #{i}] addr={addr}")


# Synthesis Verification
@pytest.mark.synthesis
def test_TIMER_OPERATION_DECODER_synthesis():
    TIMER_OPERATION_DECODER.build_vhd()


# Register Functional Tests
@pytest.mark.testcases
def test_TIMER_OPERATION_DECODER_testcases():
    TIMER_OPERATION_DECODER.test_with(tb_TIMER_OPERATION_DECODER_case_1)


# Register Stress Tests
@pytest.mark.coverage
def test_TIMER_OPERATION_DECODER_stress():
    TIMER_OPERATION_DECODER.test_with(tb_TIMER_OPERATION_DECODER_random)


# Manual Execution Entry
if __name__ == "__main__":
    lib.run_test(__file__)
