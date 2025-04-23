import os
import random

import pytest
from cocotb.binary import BinaryValue

import lib
from test_GENERICS_package import GENERICS

# -----------------------------------------------------------------------------
# Toplevel Tristate Buffer Wrapper
# -----------------------------------------------------------------------------
class TRISTATE_BUFFER_1BIT(lib.Entity):
    """This class connects the 1-bit tristate buffer entity to the test framework.
    The ports declared here correspond to the VHDL interface.
    """
    _package = GENERICS

    data_in  = lib.Entity.Input_pin   # Input: Data signal
    enable   = lib.Entity.Input_pin   # Input: Enable for driving output
    data_out = lib.Entity.Output_pin  # Output: Either data_in or 'Z'

# -----------------------------------------------------------------------------
# Functional Test: Combinatorial correctness
# -----------------------------------------------------------------------------
@TRISTATE_BUFFER_1BIT.testcase
async def tb_TRISTATE_BUFFER_1BIT_case_1(dut: TRISTATE_BUFFER_1BIT, trace: lib.Waveform):
    """Validates that the buffer outputs:
    - 'Z' when enable = 0
    - data_in when enable = 1
    """

    # Input stimuli and expected outputs
    test_vectors_data_in = ["0", "1", "0", "1"]
    test_vectors_enable  = ["0", "0", "1", "1"]
    expected_data_out    = ["Z", "Z", "0", "1"]

    # Loop through test cases
    for i, (din, en, dout_expected) in enumerate(
        zip(test_vectors_data_in, test_vectors_enable, expected_data_out), start=1
    ):
        dut.data_in.value = BinaryValue(din)
        dut.enable.value  = BinaryValue(en)

        await trace.cycle()

        yield trace.check(
            dut.data_out,
            dout_expected,
            f"Cycle {i}: data_in={din}, enable={en} -> expected data_out={dout_expected}"
        )

# -----------------------------------------------------------------------------
# Stress Test: Randomized coverage
# -----------------------------------------------------------------------------
@TRISTATE_BUFFER_1BIT.testcase
async def tb_TRISTATE_BUFFER_1BIT_coverage(dut: TRISTATE_BUFFER_1BIT, trace: lib.Waveform):
    """Performs random sampling of the tristate buffer's input space.
    Validates output for randomly selected combinations of data_in and enable.
    """

    trace.disable()  # Disable waveform capture for coverage test

    NUM_TESTS = 100
    for i in range(NUM_TESTS):
        # Randomly generate data_in and enable values
        random_data_in = random.getrandbits(1)
        random_enable  = random.getrandbits(1)

        str_data_in = str(random_data_in)
        str_enable  = str(random_enable)

        dut.data_in.value = BinaryValue(str_data_in)
        dut.enable.value  = BinaryValue(str_enable)

        await trace.cycle()

        expected = str_data_in if random_enable else "Z"

        yield trace.check(
            dut.data_out,
            expected,
            f"Test {i}: data_in={str_data_in}, enable={str_enable} -> expected data_out={expected}"
        )

# -----------------------------------------------------------------------------
# Synthesis Test: Ensure file compiles
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_TRISTATE_BUFFER_1BIT_synthesis():
    TRISTATE_BUFFER_1BIT.build_vhd()

# -----------------------------------------------------------------------------
# Manual testcase runner
# -----------------------------------------------------------------------------
@pytest.mark.testcases
def test_TRISTATE_BUFFER_1BIT_testcases():
    TRISTATE_BUFFER_1BIT.test_with(tb_TRISTATE_BUFFER_1BIT_case_1)

# -----------------------------------------------------------------------------
# Coverage test runner
# -----------------------------------------------------------------------------
@pytest.mark.coverage
def test_TRISTATE_BUFFER_1BIT_stress():
    TRISTATE_BUFFER_1BIT.test_with(tb_TRISTATE_BUFFER_1BIT_coverage)

# -----------------------------------------------------------------------------
# Direct script execution
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    lib.run_test(__file__)
