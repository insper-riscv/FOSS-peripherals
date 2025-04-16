import random
import pytest
from cocotb.binary import BinaryValue

import lib
from test_GENERICS_package import GENERICS


class GENERIC_TRISTATE_BUFFER(lib.Entity):
    _package = GENERICS

    data_in = lib.Entity.Input_pin
    enable = lib.Entity.Input_pin
    data_out = lib.Entity.Output_pin


@GENERIC_TRISTATE_BUFFER.testcase
async def tb_GENERIC_TRISTATE_BUFFER_case_1(dut: GENERIC_TRISTATE_BUFFER, trace: lib.Waveform):
    """
    Teste funcional para GENERIC_TRISTATE_BUFFER.
    - Verifica se data_out segue data_in quando enable = 1.
    - Verifica se data_out fica em alta impedância quando enable = 0.
    """

    width = len(dut.data_in)
    dut._log.info(f"Testando GENERIC_TRISTATE_BUFFER com DATA_WIDTH = {width}")

    # Dados e sinais de controle de teste
    test_vectors = [
        # Caso totalmente em alta impedância
        {"data_in": "0" * width, "enable": "0" * width, "expected_out": "Z" * width},

        # Caso totalmente igual à entrada
        {"data_in": "1" * width, "enable": "1" * width, "expected_out": "1" * width},

        # Caso parcialmente habilitado: alternância em enable (0101...)
        {
            "data_in": "1010" * (width // 4),
            "enable": "0101" * (width // 4),
            "expected_out": "".join(
                d if e == "1" else "Z"
                for d, e in zip("1010" * (width // 4), "0101" * (width // 4))
            ),
        },

        # Outro caso com enable alternando (1010...)
        {
            "data_in": "1100" * (width // 4),
            "enable": "1010" * (width // 4),
            "expected_out": "".join(
                d if e == "1" else "Z"
                for d, e in zip("1100" * (width // 4), "1010" * (width // 4))
            ),
        },
    ]

    # Executa os testes definidos acima
    for i, vec in enumerate(test_vectors, start=1):
        dut.data_in.value = BinaryValue(vec["data_in"], n_bits=width)
        dut.enable.value = BinaryValue(vec["enable"], n_bits=width)

        await trace.cycle()

        yield trace.check(
            dut.data_out,
            vec["expected_out"],
            f"Cycle {i} -> data_in={vec['data_in']}, enable={vec['enable']}, expected data_out={vec['expected_out']}"
        )


@GENERIC_TRISTATE_BUFFER.testcase
async def tb_GENERIC_TRISTATE_BUFFER_stress(dut: GENERIC_TRISTATE_BUFFER, trace: lib.Waveform):
    """
    Teste de estresse com entradas aleatórias.
    - Verifica se o comportamento está correto em diversas combinações.
    """

    trace.disable()
    width = len(dut.data_in)
    dut._log.info(f"Rodando teste de estresse com DATA_WIDTH = {width}")

    for _ in range(1000):
        rand_data_in = format(random.getrandbits(width), f"0{width}b")
        rand_enable = format(random.getrandbits(width), f"0{width}b")

        dut.data_in.value = BinaryValue(rand_data_in, n_bits=width)
        dut.enable.value = BinaryValue(rand_enable, n_bits=width)

        await trace.cycle()

        expected_out = "".join(d if e == "1" else "Z" for d, e in zip(rand_data_in, rand_enable))

        yield trace.check(
            dut.data_out,
            expected_out,
            f"Random Test -> data_in={rand_data_in}, enable={rand_enable}, expected data_out={expected_out}"
        )


@pytest.mark.synthesis
def test_GENERIC_TRISTATE_BUFFER_synthesis():
    """Testa se o componente pode ser sintetizado corretamente."""
    GENERIC_TRISTATE_BUFFER.build_vhd()


@pytest.mark.testcases
def test_GENERIC_TRISTATE_BUFFER_testcases():
    """Executa o teste funcional para 8 e 32 bits."""
    GENERIC_TRISTATE_BUFFER.test_with(tb_GENERIC_TRISTATE_BUFFER_case_1, {"DATA_WIDTH": 8})
    GENERIC_TRISTATE_BUFFER.test_with(tb_GENERIC_TRISTATE_BUFFER_case_1, {"DATA_WIDTH": 32})


@pytest.mark.coverage
def test_GENERIC_TRISTATE_BUFFER_stress_8():
    """Executa o teste de estresse para 8 bits."""
    GENERIC_TRISTATE_BUFFER.test_with(tb_GENERIC_TRISTATE_BUFFER_stress, {"DATA_WIDTH": 8})


@pytest.mark.coverage
def test_GENERIC_TRISTATE_BUFFER_stress_32():
    """Executa o teste de estresse para 32 bits."""
    GENERIC_TRISTATE_BUFFER.test_with(tb_GENERIC_TRISTATE_BUFFER_stress, {"DATA_WIDTH": 32})


if __name__ == "__main__":
    lib.run_test(__file__)
