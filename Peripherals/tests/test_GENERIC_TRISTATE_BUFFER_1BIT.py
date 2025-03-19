"""
This test file uses a structure similar to the Generic Register tests you provided.
We define an entity class for the multi-bit tristate buffer, then write testcases that
verify its functionality under different conditions (enable = 0 or 1, data_in = 0 or 1).
Finally, we provide synthesis and test-case functions using pytest markers.
"""

import random
import pytest
from cocotb.binary import BinaryValue

import lib
from test_GENERICS_package import GENERICS 

# Define supported data widths
DATA_WIDTHS = [8, 32]

# Definição de Classe
class GENERIC_TRISTATE_BUFFER(lib.Entity):
    """
    This class binds together the ports of the multi-bit tristate buffer in a way that
    the test framework can interact with. The `_package` attribute allows the test
    library to know which package definitions or parameters to associate with this entity.
    """
    _package = GENERICS

    # Linka as entradas e saidas
    data_in = lib.Entity.Input_pin    
    enable = lib.Entity.Input_pin     
    data_out = lib.Entity.Output_pin


# Teste Básico
@GENERIC_TRISTATE_BUFFER.testcase
async def tb_GENERIC_TRISTATE_BUFFER_case_1(dut: GENERIC_TRISTATE_BUFFER, trace: lib.Waveform):
    """
    This test exercises a few combinations of data_in and enable to verify that
    data_out matches data_in when enable=1, and is 'Z' (high impedance) when enable=0.
    """

    for width in DATA_WIDTHS:
        dut._log.info(f"Testing DATA_WIDTH = {width}")

        # Generate test vectors for different bit widths
        test_vectors = [
            {"data_in": "0" * width, "enable": "0" * width, "expected_out": "Z" * width},
            {"data_in": "1" * width, "enable": "1" * width, "expected_out": "1" * width},
            {"data_in": "1010" * (width // 4), "enable": "0000" * (width // 4), "expected_out": "Z" * width},
            {"data_in": "1100" * (width // 4), "enable": "1111" * (width // 4), "expected_out": "1100" * (width // 4)},
        ]

        for i, vec in enumerate(test_vectors, start=1):
            dut.data_in.value = BinaryValue(vec["data_in"])
            dut.enable.value = BinaryValue(vec["enable"])

            # Avança um clock
            await trace.cycle()

            # Checa se o valor de saída está correto
            yield trace.check(
                dut.data_out,
                vec["expected_out"],
                f"Cycle {i} -> data_in={vec['data_in']}, enable={vec['enable']}, expected data_out={vec['expected_out']}"
            )


# Teste de Carga
@GENERIC_TRISTATE_BUFFER.testcase
async def tb_GENERIC_TRISTATE_BUFFER_coverage(dut: GENERIC_TRISTATE_BUFFER, trace: lib.Waveform):
    """
    This test performs a large number of random trials to cover all possible values
    of data_in and enable. We use random tests as a demonstration of stress testing.
    """
    
    trace.disable()

    for width in DATA_WIDTHS:
        dut._log.info(f"Running stress test for DATA_WIDTH = {width}")

        qnt_tests = 1000
        for i in range(qnt_tests):
            # Gera valores aleatórios para data_in e enable
            rand_data_in = format(random.getrandbits(width), f"0{width}b")
            rand_enable = format(random.getrandbits(width), f"0{width}b")

            dut.data_in.value = BinaryValue(rand_data_in)
            dut.enable.value = BinaryValue(rand_enable)

            await trace.cycle()

            # Determina a saída esperada
            expected_out = "".join(d if e == "1" else "Z" for d, e in zip(rand_data_in, rand_enable))

            yield trace.check(
                dut.data_out,
                expected_out,
                f"Random Test #{i} with data_in={rand_data_in}, enable={rand_enable}; expected data_out={expected_out}"
            )


@pytest.mark.synthesis
def test_GENERIC_TRISTATE_BUFFER_synthesis():
    GENERIC_TRISTATE_BUFFER.build_vhd() 


@pytest.mark.testcases
def test_GENERIC_TRISTATE_BUFFER_testcases():
    GENERIC_TRISTATE_BUFFER.test_with(tb_GENERIC_TRISTATE_BUFFER_case_1)


@pytest.mark.coverage
def test_GENERIC_TRISTATE_BUFFER_stress():
    GENERIC_TRISTATE_BUFFER.test_with(tb_GENERIC_TRISTATE_BUFFER_coverage)


if __name__ == "__main__":
    lib.run_test(__file__)
