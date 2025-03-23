'''import os
import random
import pytest
from cocotb.binary import BinaryValue
import lib
from test_GENERICS_package import GENERICS

# Wrapper do VHDL com 'gpio_pin' tratado como Output
class GENERAL_DIGITAL_IO(lib.Entity):
    _package = GENERICS

    clock         = lib.Entity.Input_pin
    clear         = lib.Entity.Input_pin
    data_in       = lib.Entity.Input_pin
    write_dir     = lib.Entity.Input_pin
    read_dir      = lib.Entity.Input_pin
    write_out     = lib.Entity.Input_pin
    toggle        = lib.Entity.Input_pin
    read_out      = lib.Entity.Input_pin
    read_external = lib.Entity.Input_pin
    data_out      = lib.Entity.Output_pin
    gpio_pin      = lib.Entity.Output_pin



# Teste Básico com verificação de gpio_pin
@GENERAL_DIGITAL_IO.testcase
async def tb_output_basic(dut: GENERAL_DIGITAL_IO, trace: lib.Waveform):
    # Inicializa sinais com valores padrão
    dut.clear.value         = BinaryValue('1')
    dut.write_dir.value     = BinaryValue('0')
    dut.read_dir.value      = BinaryValue('0')
    dut.write_out.value     = BinaryValue('0')
    dut.toggle.value        = BinaryValue('0')
    dut.read_out.value      = BinaryValue('0')
    dut.read_external.value = BinaryValue('0')
    dut.data_in.value       = BinaryValue('0')

    # Aplica reset
    await trace.cycle()
    dut.clear.value = BinaryValue('0')

    # Define direção como saída
    dut.data_in.value   = BinaryValue('1')
    dut.write_dir.value = BinaryValue('1')
    await trace.cycle()
    dut.write_dir.value = BinaryValue('0')

    # Lê a direção
    dut.read_dir.value = BinaryValue('1')
    await trace.cycle()
    yield trace.check(dut.data_out, "1", "Direção deve ser 1 (Output)")
    dut.read_dir.value = BinaryValue('0')

    # Escreve 1 no pino
    dut.data_in.value = BinaryValue('1')
    dut.write_out.value = BinaryValue('1')
    await trace.cycle()
    dut.write_out.value = BinaryValue('0')

    # Lê valor da saída
    dut.read_out.value = BinaryValue('1')
    await trace.cycle()
    yield trace.check(dut.data_out, "1", "Saída deve ser 1")
    # Verifica valor do pino
    yield trace.check(dut.gpio_pin, "1", "Pino gpio_pin deve estar em 1")
    dut.read_out.value = BinaryValue('0')

    # Toggle: inverte valor de saída (1 -> 0)
    dut.data_in.value = BinaryValue('1')
    dut.toggle.value = BinaryValue('1')
    await trace.cycle()
    dut.toggle.value = BinaryValue('0')

    # Lê valor da saída
    dut.read_out.value = BinaryValue('1')
    await trace.cycle()
    yield trace.check(dut.data_out, "0", "Saída deve ter sido invertida")
    # Verifica valor do pino
    yield trace.check(dut.gpio_pin, "0", "Pino gpio_pin deve estar em 0 após toggle")
    dut.read_out.value = BinaryValue('0')

    # Toggle sem data_in (não deve fazer nada)
    dut.data_in.value = BinaryValue('0')
    dut.toggle.value = BinaryValue('1')
    await trace.cycle()
    dut.toggle.value = BinaryValue('0')
    # Lê valor da saída (esperado: ainda 0)
    dut.read_out.value = BinaryValue('1')
    await trace.cycle()
    yield trace.check(dut.data_out, "0", "Saída não deve ter sido invertida")
    # Verifica valor do pino
    yield trace.check(dut.gpio_pin, "0", "Pino gpio_pin deve permanecer 0")
    dut.read_out.value = BinaryValue('0')


# Stress test: alterna valores rapidamente com checagem do pino gpio_pin
@GENERAL_DIGITAL_IO.testcase
async def tb_output_stress(dut: GENERAL_DIGITAL_IO, trace: lib.Waveform):
    # Inicializa sinais com valores padrão
    dut.clear.value = BinaryValue('1')
    dut.write_dir.value = BinaryValue('0')
    dut.write_out.value = BinaryValue('0')
    dut.toggle.value = BinaryValue('0')
    dut.read_out.value = BinaryValue('0')
    dut.data_in.value = BinaryValue('0')

    # Aplica reset (clear = 1, depois 0)
    await trace.cycle()
    dut.clear.value = BinaryValue('0')

    # Define a direção como saída (data_in = 1, write_dir = 1)
    dut.data_in.value = BinaryValue('1')
    dut.write_dir.value = BinaryValue('1')
    await trace.cycle()
    dut.write_dir.value = BinaryValue('0')


    # Teste 1: alternância rápida de valores usando write_out
    for i in range(20):
        # Alterna entre 0 e 1 a cada ciclo
        val = BinaryValue(str(i % 2)) 
        # Define valor que será gravado no registrador de saída 
        dut.data_in.value = val       
        # Ativa gravação
        dut.write_out.value = BinaryValue('1')  
        await trace.cycle()
        # Desativa gravação
        dut.write_out.value = BinaryValue('0')  
        # Lê o valor gravado no registrador de saída
        dut.read_out.value = BinaryValue('1')
        await trace.cycle()
        yield trace.check(dut.data_out, str(i % 2), f"Erro de escrita rápida no ciclo {i}")
        # Verifica também o valor do pino gpio_pin
        yield trace.check(dut.gpio_pin, str(i % 2), f"Pino gpio_pin incorreto no ciclo {i}")
        dut.read_out.value = BinaryValue('0')

    # Teste 2: toggles consecutivos usando o sinal de toggle
    dut.data_in.value = BinaryValue('1')  # Toggle só é ativado se data_in = 1
    expected = int(dut.data_out.value.binstr)  # Valor atual esperado no registrador

    for i in range(10):
        # Ativa toggle (inversão do valor no registrador de saída)
        dut.toggle.value = BinaryValue('1')
        await trace.cycle()
        dut.toggle.value = BinaryValue('0')
        

        # Atualiza valor esperado (0 -> 1 ou 1 -> 0)
        expected = 1 - expected

        # Lê valor do registrador e compara com esperado
        dut.read_out.value = BinaryValue('1')
        await trace.cycle()
        yield trace.check(dut.data_out, str(expected), f"Erro de toggle no ciclo {i}")
        # Verifica valor no pino gpio_pin
        yield trace.check(dut.gpio_pin, str(expected), f"Pino gpio_pin incorreto após toggle no ciclo {i}")
        dut.read_out.value = BinaryValue('0')



# Build para síntese
@pytest.mark.synthesis
def test_GENERAL_DIGITAL_IO_synthesis():
    GENERAL_DIGITAL_IO.build_vhd()

# Pytest wrappers
@pytest.mark.testcases
def test_output_basic():
    GENERAL_DIGITAL_IO.test_with(tb_output_basic)

@pytest.mark.testcases
def test_output_stress():
    GENERAL_DIGITAL_IO.test_with(tb_output_stress)

# Execução direta
if __name__ == "__main__":
    lib.run_test(__file__)'''

import os
import random
import pytest
from cocotb.binary import BinaryValue
import lib
from test_GENERICS_package import GENERICS

class GENERAL_DIGITAL_IO(lib.Entity):
    _package = GENERICS

    clock         = lib.Entity.Input_pin
    clear         = lib.Entity.Input_pin
    data_in       = lib.Entity.Input_pin
    write_dir     = lib.Entity.Input_pin
    read_dir      = lib.Entity.Input_pin
    write_out     = lib.Entity.Input_pin
    toggle        = lib.Entity.Input_pin
    read_out      = lib.Entity.Input_pin
    read_external = lib.Entity.Input_pin
    data_out      = lib.Entity.Output_pin
    gpio_pin      = lib.Entity.Input_pin  # Neste contexto, gpio_pin atua como entrada

@GENERAL_DIGITAL_IO.testcase
async def tb_input_basic(dut: GENERAL_DIGITAL_IO, trace: lib.Waveform):
    # Teste de leitura da entrada com sincronização (aguarda 2 ciclos após mudança em gpio_pin)
    yield trace.check(dut.data_out, "Z", "Saida Inicial deve ser Z.")

    # Inicializa sinais
    dut.clear.value         = BinaryValue('0')
    dut.write_dir.value     = BinaryValue('0')
    dut.read_dir.value      = BinaryValue('0')
    dut.write_out.value     = BinaryValue('0')
    dut.toggle.value        = BinaryValue('0')
    dut.read_out.value      = BinaryValue('0')
    dut.read_external.value = BinaryValue('0')
    dut.data_in.value       = BinaryValue('0')

    # Define direção como entrada
    dut.data_in.value = BinaryValue('0')
    dut.write_dir.value = BinaryValue('1')
    await trace.cycle()
    yield trace.check(dut.data_out, "Z", "Saida Escrita de direção deve ser Z.")
    dut.write_dir.value = BinaryValue('0')

    # Lê direção
    dut.read_dir.value = BinaryValue('1')
    await trace.cycle()
    yield trace.check(dut.data_out, "0", "Direção deve ser 0 (Input)")
    dut.read_dir.value = BinaryValue('0')

    # Ativa leitura do pino externo
    dut.read_external.value = BinaryValue('1')

    # Testa leitura de 0
    dut.gpio_pin.value = BinaryValue('0')
    await trace.cycle()
    yield trace.check(dut.data_out, "Z", "Saida deve ser Z por não ter atualizado ainda.")
    await trace.cycle()
    yield trace.check(dut.data_out, "0", "gpio_pin=0 deve refletir em data_out")

    # Testa leitura de 1
    dut.gpio_pin.value = BinaryValue('1')
    await trace.cycle()
    yield trace.check(dut.data_out, "0", "gpio_pin=0 deve refletir em data_out por não ter atualizado ainda")
    await trace.cycle()
    yield trace.check(dut.data_out, "1", "gpio_pin=1 deve refletir em data_out")

    dut.read_external.value = BinaryValue('0')
    
@GENERAL_DIGITAL_IO.testcase
async def tb_input_stress(dut: GENERAL_DIGITAL_IO, trace: lib.Waveform):
    """
    Teste de estresse: altera `gpio_pin` e verifica se `data_out` reflete o valor com 1 ciclo de atraso.
    """

    # Inicializa sinais
    dut.clear.value         = BinaryValue('0')
    dut.write_dir.value     = BinaryValue('0')
    dut.read_dir.value      = BinaryValue('0')
    dut.write_out.value     = BinaryValue('0')
    dut.toggle.value        = BinaryValue('0')
    dut.read_out.value      = BinaryValue('0')
    dut.read_external.value = BinaryValue('1') 
    dut.data_in.value       = BinaryValue('0')

    # Configura direção como entrada
    dut.write_dir.value = BinaryValue('1')
    await trace.cycle()
    dut.write_dir.value = BinaryValue('0')

    # Espera DUT estabilizar
    await trace.cycle()

    # Lista de valores esperados, com atraso de 1 ciclo
    expected_history = []

    num_changes = 100

    for i in range(num_changes):
        new_value = random.choice(['0', '1'])
        dut.gpio_pin.value = BinaryValue(new_value)
        #Espera estabilização
        await trace.cycle()
        await trace.cycle()
        expected_history.append(new_value)
        expected = expected_history[-1]
        #Checa se teve pelo menos duas iterações
        if i >= 2:
            yield trace.check(
                dut.data_out,
                expected,
                f"[Ciclo {i}] Esperado data_out={expected}, gpio_pin={new_value}"
            )

@pytest.mark.synthesis
def test_GENERAL_DIGITAL_IO_synthesis():
    # Teste de síntese para verificar se o código VHDL pode ser compilado
    GENERAL_DIGITAL_IO.build_vhd()

@pytest.mark.testcases
def test_input_basic():
    # Executa o teste básico de entrada
    GENERAL_DIGITAL_IO.test_with(tb_input_basic)

@pytest.mark.testcases
def test_input_stress():
    # Executa o teste de stress de entrada
    GENERAL_DIGITAL_IO.test_with(tb_input_stress)

if __name__ == "__main__":
    # Execução direta do arquivo
    lib.run_test(__file__)

