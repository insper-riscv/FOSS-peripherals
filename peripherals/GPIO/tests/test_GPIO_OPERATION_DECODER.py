import cocotb
from cocotb.triggers import RisingEdge
from cocotb.binary import BinaryValue
import pytest
import lib

class GPIO_OPERATION_DECODER(lib.Entity):
    """
    Class representing the updated GPIO_OPERATION_DECODER module.
    """
    address = lib.Entity.Input_pin
    dir_enable = lib.Entity.Output_pin
    write_op = lib.Entity.Output_pin
    read_op = lib.Entity.Output_pin

# Basic Test Case
@GPIO_OPERATION_DECODER.testcase
async def tb_GPIO_OPERATION_DECODER_case_1(dut: GPIO_OPERATION_DECODER, trace: lib.Waveform):
    """
    Basic test for GPIO_OPERATION_DECODER checking the outputs for each address.
    """
    test_vectors = [
        # address, dir_enable, write_op, read_op
        ("000", '1', "00", "11"),  # Direction enable
        ("001", '0', "00", "11"),  # Write operation 0
        ("010", '0', "01", "11"),  # Write operation 1
        ("011", '0', "10", "11"),  # Write operation 2
        ("100", '0', "11", "11"),  # Write operation 3
        ("101", '0', "00", "00"),  # Read operation 0
        ("110", '0', "00", "01"),  # Read operation 1
        ("111", '0', "00", "10"),  # Read operation 2
    ]

    for i, (addr, expected_dir, expected_write, expected_read) in enumerate(test_vectors, start=1):
        dut.address.value = BinaryValue(addr)
        await trace.cycle()

        yield trace.check(dut.dir_enable, expected_dir,
                          f"Test #{i}: address={addr}, expected dir_enable={expected_dir}")
        yield trace.check(dut.write_op, expected_write,
                          f"Test #{i}: address={addr}, expected write_op={expected_write}")
        yield trace.check(dut.read_op, expected_read,
                          f"Test #{i}: address={addr}, expected read_op={expected_read}")

# Randomized Test
@GPIO_OPERATION_DECODER.testcase
async def tb_GPIO_OPERATION_DECODER_random(dut: GPIO_OPERATION_DECODER, trace: lib.Waveform):
    """
    Stress test the GPIO_OPERATION_DECODER using randomized address values.
    """
    trace.disable()
    import random
    
    for i in range(100):
        addr_int = random.randint(0, 7)
        addr = format(addr_int, '03b')

        # Expected logic
        if addr == "000":
            dir_expected = '1'
        else:
            dir_expected = '0'

        write_map = {
            "001": "00",
            "010": "01",
            "011": "10",
            "100": "11",
        }
        write_expected = write_map.get(addr, "00")

        read_map = {
            "101": "00",
            "110": "01",
            "111": "10",
        }
        read_expected = read_map.get(addr, "11")

        dut.address.value = BinaryValue(addr)
        await trace.cycle()

        yield trace.check(dut.dir_enable, dir_expected,
                          f"Random Test #{i}: address={addr}, expected dir_enable={dir_expected}")
        yield trace.check(dut.write_op, write_expected,
                          f"Random Test #{i}: address={addr}, expected write_op={write_expected}")
        yield trace.check(dut.read_op, read_expected,
                          f"Random Test #{i}: address={addr}, expected read_op={read_expected}")

# Synthesis Test
@pytest.mark.synthesis
def test_GPIO_OPERATION_DECODER_synthesis():
    GPIO_OPERATION_DECODER.build_vhd()

# Basic Test Case Entry
@pytest.mark.testcases
def test_GPIO_OPERATION_DECODER_testcases():
    GPIO_OPERATION_DECODER.test_with(tb_GPIO_OPERATION_DECODER_case_1)

# Stress Test Entry
@pytest.mark.coverage
def test_GPIO_OPERATION_DECODER_stress():
    GPIO_OPERATION_DECODER.test_with(tb_GPIO_OPERATION_DECODER_random)

# Local run
if __name__ == "__main__":
    lib.run_test(__file__)
