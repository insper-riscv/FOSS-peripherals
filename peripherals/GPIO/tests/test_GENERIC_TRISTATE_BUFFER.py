import random
import pytest
from cocotb.binary import BinaryValue

import lib
from test_GENERICS_package import GENERICS


# Classe que representa a entidade VHDL GENERIC_TRISTATE_BUFFER
class GENERIC_TRISTATE_BUFFER(lib.Entity):
    _package = GENERICS  # Associa a entidade a um pacote de parâmetros

    # Definição das portas de entrada e saída do buffer triestado
    data_in = lib.Entity.Input_pin  # Entrada de dados
    enable = lib.Entity.Input_pin   # Sinal de habilitação
    data_out = lib.Entity.Output_pin  # Saída de dados


# Teste funcional básico para o buffer triestado
@GENERIC_TRISTATE_BUFFER.testcase
async def tb_GENERIC_TRISTATE_BUFFER_case_1(dut: GENERIC_TRISTATE_BUFFER, trace: lib.Waveform):
    """
    Teste funcional para GENERIC_TRISTATE_BUFFER.
    - Verifica se a saída segue a entrada quando enable = 1.
    - Garante que a saída é alta impedância (Z) quando enable = 0.
    """
    # Obtém a largura do barramento de dados
    width = len(dut.data_in)  
    dut._log.info(f"Testando GENERIC_TRISTATE_BUFFER com DATA_WIDTH = {width}")

    # Combinações de entrada, enable e saidas esperadas
    test_vectors = [
        # Caso alta impedância
        {"data_in": "0" * width, "enable": "0" * width, "expected_out": "Z" * width}, 
        # Caso em que a saída deve seguir a entrada 
        {"data_in": "1" * width, "enable": "1" * width, "expected_out": "1" * width}, 
        # Caso alta impedância alternada (algumas partes ativas, outras em Z)
        {"data_in": "1010" * (width // 4), "enable": "0101" * (width // 4), "expected_out": "".join(
            d if e == "1" else "Z" for d, e in zip("1010" * (width // 4), "0101" * (width // 4))
        )},
        # Caso alta impedância alternada v2 (algumas partes ativas, outras em Z)
        {"data_in": "1100" * (width // 4), "enable": "1010" * (width // 4), "expected_out": "".join(
            d if e == "1" else "Z" for d, e in zip("1100" * (width // 4), "1010" * (width // 4))
        )},
    ]

    # Testa os testes manuais
    for i, vec in enumerate(test_vectors, start=1):
        # Define os valores de entrada e enable
        dut.data_in.value = BinaryValue(vec["data_in"], n_bits=width)
        dut.enable.value = BinaryValue(vec["enable"], n_bits=width)
        # Avança um clock
        await trace.cycle() 

        # Verifica se a saída corresponde ao esperado
        yield trace.check(
            dut.data_out,
            vec["expected_out"],
            f"Cycle {i} -> data_in={vec['data_in']}, enable={vec['enable']}, expected data_out={vec['expected_out']}"
        )


# Teste de estresse para cobrir diferentes cenários com valores aleatórios
@GENERIC_TRISTATE_BUFFER.testcase
async def tb_GENERIC_TRISTATE_BUFFER_stress(dut: GENERIC_TRISTATE_BUFFER, trace: lib.Waveform):
    """
    Teste de estresse para GENERIC_TRISTATE_BUFFER com valores aleatórios.
    - Garante a cobertura de todas as possíveis combinações de entrada e enable.
    - Executa o teste para larguras de 8 e 32 bits.
    """
    # Desativa rastreamento detalhado para evitar logs excessivos
    trace.disable()
    # Obtém a largura real do dado de entrada
    width = len(dut.data_in) 

    dut._log.info(f"Executando teste de estresse para GENERIC_TRISTATE_BUFFER com DATA_WIDTH = {width}")
    # Executa 1000 iterações com valores aleatórios
    for _ in range(1000):
        # Gera valor aleatório de entrada
        rand_data_in = format(random.getrandbits(width), f"0{width}b")
        # Gera sinal enable aleatório
        rand_enable = format(random.getrandbits(width), f"0{width}b") 

        # Define os valores de entrada
        dut.data_in.value = BinaryValue(rand_data_in, n_bits=width)
        dut.enable.value = BinaryValue(rand_enable, n_bits=width)
        
        #Avança um clock
        await trace.cycle()

        # Calcula a saída esperada: segue a entrada se enable=1, caso contrário é 'Z'
        expected_out = "".join(d if e == "1" else "Z" for d, e in zip(rand_data_in, rand_enable))

        # Verifica se a saída está correta
        yield trace.check(
            dut.data_out,
            expected_out,
            f"Teste Aleatório -> data_in={rand_data_in}, enable={rand_enable}, expected data_out={expected_out}"
        )


# Teste de síntese para verificar se o design pode ser sintetizado corretamente
@pytest.mark.synthesis
def test_GENERIC_TRISTATE_BUFFER_synthesis():
    """Testa a síntese."""
    GENERIC_TRISTATE_BUFFER.build_vhd()


# Executa os testes funcionais para 8 e 32 bits
@pytest.mark.testcases
def test_GENERIC_TRISTATE_BUFFER_testcases():
    """Executa os testes funcionais para as larguras de 8 e 32 bits."""
    GENERIC_TRISTATE_BUFFER.test_with(tb_GENERIC_TRISTATE_BUFFER_case_1, {"DATA_WIDTH": 8})
    GENERIC_TRISTATE_BUFFER.test_with(tb_GENERIC_TRISTATE_BUFFER_case_1, {"DATA_WIDTH": 32})


# Executa os testes de estresse para garantir cobertura em 8 bits
@pytest.mark.coverage
def test_GENERIC_TRISTATE_BUFFER_stress_8():
    """Executa teste de estresse para DATA_WIDTH=8."""
    GENERIC_TRISTATE_BUFFER.test_with(tb_GENERIC_TRISTATE_BUFFER_stress, {"DATA_WIDTH": 8})

# Executa os testes de estresse para garantir cobertura em 32 bits
@pytest.mark.coverage
def test_GENERIC_TRISTATE_BUFFER_stress_32():
    """Executa teste de estresse para DATA_WIDTH=32."""
    GENERIC_TRISTATE_BUFFER.test_with(tb_GENERIC_TRISTATE_BUFFER_stress, {"DATA_WIDTH": 32})


if __name__ == "__main__":
    lib.run_test(__file__)
