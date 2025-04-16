import pytest
import lib
from test_GENERICS_package import GENERICS

from cocotb.binary import BinaryValue

# -----------------------------------------------------------------------------
# Toplevel Timer
# -----------------------------------------------------------------------------
class TIMER(lib.Entity):
    _package = GENERICS

    clock     = lib.Entity.Input_pin
    clear     = lib.Entity.Input_pin
    data_in   = lib.Entity.Input_pin
    address   = lib.Entity.Input_pin
    write     = lib.Entity.Input_pin
    read      = lib.Entity.Input_pin
    data_out  = lib.Entity.Output_pin


# -----------------------------------------------------------------------------
# Endereços das Operações
# -----------------------------------------------------------------------------
ADDR = {
    "start":    "0000",
    "load_rst": "0001",
    "load":      "0010",
    "reset":     "0011",
    "read_ovf": "0100",
    "read_val": "0101",
    "nop":      "1111"
}


# -----------------------------------------------------------------------------
# Função auxiliar para aplicar operações ao Timer
# -----------------------------------------------------------------------------
async def timer_op(dut, trace, op, data_in=None, write=False, read=False):
    """
    Aplica uma operação ao Timer, simulando um ciclo completo de barramento:
    1. Configura o endereço (address).
    2. Configura os sinais de controle (write, read).
    3. Escreve no barramento de dados, se necessário.
    4. Aguarda um ciclo de clock para efetivar a operação.
    5. Desativa os sinais de controle.
    """
    # 1. Endereço
    dut.address.value = BinaryValue(ADDR[op], n_bits=4)
    # 2. Sinais de controle
    dut.write.value   = BinaryValue('1' if write else '0')
    dut.read.value    = BinaryValue('1' if read else '0')
    # 3. Barramento de Dados
    if data_in is not None:
        dut.data_in.value = BinaryValue(format(data_in, '032b'))
    # 4. Clock
    await trace.cycle()
    # 5. Limpeza dos Sinais
    dut.write.value = BinaryValue('0')
    dut.read.value  = BinaryValue('0')

# -----------------------------------------------------------------------------
# Teste Manual 
# -----------------------------------------------------------------------------
@TIMER.testcase
async def tb_timer_manual(dut: TIMER, trace: lib.Waveform):
    """
    Teste estendido do TIMER validando:
    1) Clear Periférico
    2) Configuração de valor de reset (load_rst)
    3) Operação de load (carregar valor do data_in diretamente no contador) e leitura do contador
    4) Operação de reínicio (reinícia o contador) e leitura do contador
    5) Operação de start e incrementa por alguns ciclos
    6) Operação de stop e vê se incremento é interrompido
    """

    # 1. Clear
    dut.clear.value = BinaryValue('1')
    await trace.cycle()
    dut.clear.value = BinaryValue('0')

    # 2. Configura o valor de reset (0x10)
    await timer_op(dut, trace, "load_rst", data_in=0x10, write=True)

    # 3. Carraga valor (0x15) para o contador
    await timer_op(dut, trace, "load", data_in=0x15,write=True)

    # Lê o valor atual do contador e verifica se está em 0x15
    await timer_op(dut, trace, "read_val", read=True)
    yield trace.check(
        dut.data_out,
        format(0x15, '032b'),
        "O contador deve refletir o valor de reset (0x15)."
    )

    # 4. Reinicia o contador (Deve voltar para 0x10)
    await timer_op(dut, trace, "reset",write=True)
    # Lê o valor atual do contador e verifica se está em 0x10
    await timer_op(dut, trace, "read_val", read=True)
    yield trace.check(
        dut.data_out,
        format(0x10, '032b'),
        "O contador deve refletir o valor de reset (0x10)."
    )
    # 5. Começa o Contador e incrementa ele por 6 loops. 4 clocks, mais o clock de leitura e clock de start
    await timer_op(dut, trace, "start", data_in=0x1,write=True)
    for i in range(4):
        await trace.cycle()
    await timer_op(dut, trace, "read_val", read=True)  
    yield trace.check(
        dut.data_out,
        format(0x16, '032b'),
        f"O contador deve ser 0x16."
    )
    # 6) Interrompe o relógio e checa se não há incremento. Deve ser 0x17 pelo clock de início.
    await timer_op(dut, trace, "start", data_in=0x0,write=True)
    for i in range(4):
        await trace.cycle()
    await timer_op(dut, trace, "read_val", read=True)  
    yield trace.check(
        dut.data_out,
        format(0x17, '032b'),
        f"O contador deve ser 0x17."
    )
        

# -----------------------------------------------------------------------------
# Teste de síntese
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_TIMER_synthesis():
    TIMER.build_vhd()


# -----------------------------------------------------------------------------
# Teste Manual Timer
# -----------------------------------------------------------------------------
@pytest.mark.testcases
def test_timer_manual():
    TIMER.test_with(tb_timer_manual)


# -----------------------------------------------------------------------------
# Execução direta
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    lib.run_test(__file__)
