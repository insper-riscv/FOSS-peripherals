import cocotb
from cocotb.triggers import RisingEdge
from cocotb.binary import BinaryValue
import pytest
import lib

class GPIO_OPERATION_DECODER(lib.Entity):
    """
    Class representing the GPIO_OPERATION_DECODER module.
    """
    address = lib.Entity.Input_pin
    write = lib.Entity.Input_pin
    read = lib.Entity.Input_pin
    data_out = lib.Entity.Output_pin

# Basic Test Case
@GPIO_OPERATION_DECODER.testcase
async def tb_GPIO_OPERATION_DECODER_case_1(dut: GPIO_OPERATION_DECODER, trace: lib.Waveform):
    """
    Tests the GPIO_OPERATION_DECODER by checking expected output for various address and control signal combinations.
    """
    test_vectors = [
        ("000", 1, 0, "00000001"),  # Write Direction
        ("001", 0, 1, "00000010"),  # Read Direction
        ("010", 1, 0, "00000100"),  # Write Output
        ("011", 1, 0, "00001000"),  # Toggle Output
        ("100", 0, 1, "00010000"),  # Read Output
        ("101", 0, 1, "00100000"),  # Read Pin
        ("110", 1, 0, "00000000"),  # Invalid Address
        ("111", 0, 1, "00000000")   # Invalid Address
    ]

    for i, (addr, wr, rd, expected) in enumerate(test_vectors, start=1):
        dut.address.value = BinaryValue(addr)
        dut.write.value = BinaryValue(str(wr))
        dut.read.value = BinaryValue(str(rd))
        await trace.cycle()
        
        yield trace.check(
            dut.data_out,
            expected,
            f"Test #{i}: address={addr}, write={wr}, read={rd}, expected data_out={expected}"
        )

# Randomized Test Case
@GPIO_OPERATION_DECODER.testcase
async def tb_GPIO_OPERATION_DECODER_random(dut: GPIO_OPERATION_DECODER, trace: lib.Waveform):
    """
    Stress test the GPIO_OPERATION_DECODER using randomized address and control signals.
    """
    trace.disable()
    import random
    
    for i in range(100):
        addr = format(random.randint(0, 7), '03b')
        wr = random.randint(0, 1)
        rd = random.randint(0, 1)
        
        expected_out = ["0"] * 8  # From bit 7 down to 0

        bit_map = {
            "000": (0, "write"),  # Write Direction
            "001": (1, "read"),   # Read Direction
            "010": (2, "write"),  # Write Output
            "011": (3, "write"),  # Toggle Output
            "100": (4, "read"),   # Read Output
            "101": (5, "read")    # Read Pin
        }

        if addr in bit_map:
            bit_index, required = bit_map[addr]
            if (required == "write" and wr) or (required == "read" and rd):
                expected_out[7 - bit_index] = "1"  # align with data_out(7 downto 0)

        dut.address.value = BinaryValue(addr)
        dut.write.value = BinaryValue(str(wr))
        dut.read.value = BinaryValue(str(rd))
        await trace.cycle()
        
        yield trace.check(
            dut.data_out,
            "".join(expected_out),
            f"Random Test #{i}: address={addr}, write={wr}, read={rd}, expected data_out={''.join(expected_out)}"
        )

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
