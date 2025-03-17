import os
import random

import pytest
from cocotb.binary import BinaryValue

import lib  # Your testing library
from test_GENERICS_package import GENERICS  # Your package of GENERICS

# ------------------------------------------------------------------------------
# 1. Specify VHDL File Path (Customizable)
# ------------------------------------------------------------------------------
VHDL_FILE_PATH = os.path.join("vhdl_files", "generic_tristate_buffer.vhd")  # Customize this path if needed

# ------------------------------------------------------------------------------
# 2. Entity Class Definition
# ------------------------------------------------------------------------------
class GENERIC_TRISTATE_BUFFER(lib.Entity):
    """
    This class represents a generic tristate buffer in Python for testing.
    The VHDL file is explicitly specified to avoid auto-detection issues.
    """
    _package = GENERICS  # Link with GENERICS package if needed

    # Explicitly provide the VHDL file path
    vhdl_file = VHDL_FILE_PATH  

    # Define entity ports:
    data_in = lib.Entity.Input_vector  # Multi-bit data input
    enable = lib.Entity.Input_vector   # Multi-bit enable control
    data_out = lib.Entity.Inout_vector # Multi-bit inout pin (tristate behavior)

# ------------------------------------------------------------------------------
# 3. Basic Functional Testcase
# ------------------------------------------------------------------------------
@GENERIC_TRISTATE_BUFFER.testcase
async def tb_TRISTATE_BUFFER_case_1(dut: GENERIC_TRISTATE_BUFFER, trace: lib.Waveform):
    """
    Basic test to verify the tristate buffer behavior with different inputs.
    """
    DATA_WIDTH = 8  # Modify this if needed
    
    test_vectors_data_in = ["00000000", "11111111", "10101010", "01010101"]
    test_vectors_enable  = ["00000000", "11111111", "10101010", "01010101"]
    expected_data_out    = ["ZZZZZZZZ", "11111111", "10101010", "ZZZZZZZZ"]  

    for i, (din, en, dout_expected) in enumerate(
        zip(test_vectors_data_in, test_vectors_enable, expected_data_out), start=1
    ):
        dut.data_in.value = BinaryValue(din)
        dut.enable.value = BinaryValue(en)

        await trace.cycle()

        yield trace.check(
            dut.data_out,
            dout_expected,
            f"Cycle {i} -> data_in={din}, enable={en}, expected data_out={dout_expected}"
        )

# ------------------------------------------------------------------------------
# 4. Coverage / Stress Testcase
# ------------------------------------------------------------------------------
@GENERIC_TRISTATE_BUFFER.testcase
async def tb_TRISTATE_BUFFER_coverage(dut: GENERIC_TRISTATE_BUFFER, trace: lib.Waveform):
    """
    Large coverage test with random values.
    """
    trace.disable()

    DATA_WIDTH = 8  # Modify this if needed
    qnt_tests = 1000  

    for i in range(qnt_tests):
        random_data_in = format(random.getrandbits(DATA_WIDTH), f'0{DATA_WIDTH}b')
        random_enable = format(random.getrandbits(DATA_WIDTH), f'0{DATA_WIDTH}b')

        dut.data_in.value = BinaryValue(random_data_in)
        dut.enable.value = BinaryValue(random_enable)

        await trace.cycle()

        expected = ''.join(d if e == '1' else 'Z' for d, e in zip(random_data_in, random_enable))

        yield trace.check(
            dut.data_out,
            expected,
            f"Test #{i} with data_in={random_data_in}, enable={random_enable}; expected data_out={expected}"
        )

# ------------------------------------------------------------------------------
# 5. Pytest Hooks for Building and Running
# ------------------------------------------------------------------------------
@pytest.mark.synthesis
def test_TRISTATE_BUFFER_synthesis():
    """
    Explicitly build the VHDL file from the provided path.
    """
    GENERIC_TRISTATE_BUFFER.build_vhd(vhdl_file=VHDL_FILE_PATH)        
    GENERIC_TRISTATE_BUFFER.build_netlistsvg()  

@pytest.mark.testcases
def test_TRISTATE_BUFFER_testcases():
    """
    Run the basic functional test.
    """
    GENERIC_TRISTATE_BUFFER.test_with(tb_TRISTATE_BUFFER_case_1)

@pytest.mark.coverage
def test_TRISTATE_BUFFER_stress():
    """
    Run the stress test.
    """
    GENERIC_TRISTATE_BUFFER.test_with(tb_TRISTATE_BUFFER_coverage)

# ------------------------------------------------------------------------------
# 6. Main Entry Point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Run the test file directly.
    """
    lib.run_test(__file__)
