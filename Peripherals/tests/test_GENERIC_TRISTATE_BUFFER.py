import os
import random
import pytest
from cocotb.binary import BinaryValue

import lib  
from test_GENERICS_package import GENERICS 

class GENERIC_TRISTATE_BUFFER(lib.Entity):
    """
    Binds to the multi-bit VHDL entity.
    """
    _package = GENERICS
    data_in  = lib.Entity.Input_pin
    enable   = lib.Entity.Input_pin
    data_out = lib.Entity.Output_pin


@GENERIC_TRISTATE_BUFFER.testcase
async def tb_TRISTATE_BUFFER_case_1(dut, trace):
    test_vectors_data_in = [
        "00000000",
        "11111111",
        "10101010",
        "01010101"
    ]
    test_vectors_enable = [
        "00000000", 
        "11111111",
        "11111111",
        "00000000"
    ]
    expected_data_out = [
        "ZZZZZZZZ",
        "11111111",
        "10101010",
        "ZZZZZZZZ"
    ]

    for i, (din, en, dout_expected) in enumerate(
        zip(test_vectors_data_in, test_vectors_enable, expected_data_out), start=1
    ):
        dut.data_in.value = BinaryValue(din)
        dut.enable.value  = BinaryValue(en)

        await trace.cycle()

        yield trace.check(
            dut.data_out,
            dout_expected,
            f"Cycle {i} -> data_in={din}, enable={en}, expected data_out={dout_expected}"
        )



@GENERIC_TRISTATE_BUFFER.testcase
async def tb_TRISTATE_BUFFER_coverage(dut: GENERIC_TRISTATE_BUFFER, trace: lib.Waveform):
    """
    Large coverage test with random 8-bit patterns.
    """
    trace.disable()

    DATA_WIDTH = 8 
    qnt_tests  = 1000  

    for i in range(qnt_tests):
        random_data_in = format(random.getrandbits(DATA_WIDTH), f'0{DATA_WIDTH}b')
        random_enable  = format(random.getrandbits(DATA_WIDTH), f'0{DATA_WIDTH}b')

        dut.data_in.value = BinaryValue(random_data_in)
        dut.enable.value  = BinaryValue(random_enable)

        await trace.cycle()

        expected = ''.join(
            (d if e == '1' else 'Z')
            for d, e in zip(random_data_in, random_enable)
        )

        yield trace.check(
            dut.data_out,
            expected,
            f"Test #{i}: data_in={random_data_in}, enable={random_enable}, expected={expected}"
        )


@pytest.mark.synthesis
def test_TRISTATE_BUFFER_synthesis():
    """
    Build the multi-bit VHDL buffer,
    which implicitly also requires the 1-bit buffer source.
    """
    GENERIC_TRISTATE_BUFFER.build_vhd()
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
    Run the random coverage test.
    """
    GENERIC_TRISTATE_BUFFER.test_with(tb_TRISTATE_BUFFER_coverage)

if __name__ == "__main__":
    lib.run_test(__file__)
