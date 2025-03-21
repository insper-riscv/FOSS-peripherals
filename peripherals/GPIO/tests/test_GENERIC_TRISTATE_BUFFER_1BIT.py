"""
This test file uses a structure similar to the Generic Register tests you provided.
We define an entity class for the 1‑bit tristate buffer, then write testcases that
verify its functionality under different conditions (enable = 0 or 1, data_in = 0 or 1).
Finally, we provide synthesis and test-case functions using pytest markers.
"""

import os
import random

import pytest
from cocotb.binary import BinaryValue

import lib
from test_GENERICS_package import GENERICS 

# Definição de Classe
class GENERIC_TRISTATE_BUFFER_1BIT(lib.Entity):
    """
    This class binds together the ports of our 1‑bit tristate buffer in a way that
    the test framework can interact with. The `_package` attribute allows the test
    library to know which package definitions or parameters to associate with this entity.
    """

    # Linka as entradas e saidas
    data_in = lib.Entity.Input_pin    
    enable = lib.Entity.Input_pin     
    data_out = lib.Entity.Output_pin


# Teste Básico
@GENERIC_TRISTATE_BUFFER_1BIT.testcase
async def tb_TRISTATE_BUFFER_1BIT_case_1(dut: GENERIC_TRISTATE_BUFFER_1BIT, trace: lib.Waveform):
    """
    This test exercises a few combinations of data_in and enable to verify that
    data_out matches data_in when enable=1, and is 'Z' (high impedance) when enable=0.
    """

    # Define as entradas a serem testadas e as saidas esperadas para cada entrada
    test_vectors_data_in = ["0", "1", "0", "1"]
    test_vectors_enable  = ["0", "0", "1", "1"]
    expected_data_out    = ["Z", "Z", "0", "1"] 

    # Testa as combinações básicas propostas
    for i, (din, en, dout_expected) in enumerate(
        zip(test_vectors_data_in, test_vectors_enable, expected_data_out), start=1
    ):
        # Coloca as entradas atuais
        dut.data_in.value = BinaryValue(din)
        dut.enable.value = BinaryValue(en)

        # Avança um clock
        await trace.cycle()

        # Checa se o valor de saida está correto
        yield trace.check(
            dut.data_out,
            dout_expected,
            f"Cycle {i} -> data_in={din}, enable={en}, expected data_out={dout_expected}"
        )


# Teste de Carga
@GENERIC_TRISTATE_BUFFER_1BIT.testcase
async def tb_TRISTATE_BUFFER_1BIT_coverage(dut: GENERIC_TRISTATE_BUFFER_1BIT, trace: lib.Waveform):
    """
    This test performs a large number of random trials to cover all possible values
    of data_in and enable. Although there are only 2 bits, we use random tests as
    a demonstration of stress testing in a similar style to the generic register test.
    """
    
    trace.disable()

    # Número de testes
    qnt_tests = 1000
    for i in range(qnt_tests):
        # Gera bits aleatorios para data_in e enable
        random_data_in = random.getrandbits(1)
        random_enable = random.getrandbits(1)

        # Converte a entrada para string
        str_data_in = str(random_data_in)
        str_enable = str(random_enable)

        # Coloca os valores de entrada
        dut.data_in.value = BinaryValue(str_data_in)
        dut.enable.value = BinaryValue(str_enable)

        # Espera o próximo clock
        await trace.cycle()

        # Determina o output esperadp
        if random_enable == 1:
            expected = str_data_in
        else:
            expected = "Z"

        # Checa os resultados
        yield trace.check(
            dut.data_out,
            expected,
            f"Test #{i} with data_in={str_data_in}, enable={str_enable}; expected data_out={expected}"
        )


@pytest.mark.synthesis
def test_TRISTATE_BUFFER_1BIT_synthesis():
    GENERIC_TRISTATE_BUFFER_1BIT.build_vhd() 


@pytest.mark.testcases
def test_TRISTATE_BUFFER_1BIT_testcases():
    GENERIC_TRISTATE_BUFFER_1BIT.test_with(tb_TRISTATE_BUFFER_1BIT_case_1)


@pytest.mark.coverage
def test_TRISTATE_BUFFER_1BIT_stress():
    GENERIC_TRISTATE_BUFFER_1BIT.test_with(tb_TRISTATE_BUFFER_1BIT_coverage)


if __name__ == "__main__":
    lib.run_test(__file__)