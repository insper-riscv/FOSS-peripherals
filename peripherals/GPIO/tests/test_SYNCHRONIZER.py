import os
import random
import pytest
from cocotb.binary import BinaryValue
import lib
from test_GENERICS_package import GENERICS


# Classe da Entidade SYNCHRONIZER
class SYNCHRONIZER(lib.Entity):
    """
    Classe que representa o componente SYNCHRONIZER com dois flip-flops.
    """
    _package = GENERICS
    clock = lib.Entity.Input_pin
    async_in = lib.Entity.Input_pin
    sync_out = lib.Entity.Output_pin


# Teste Básico – verifica funcionamento com mudanças previsíveis
@SYNCHRONIZER.testcase
async def tb_SYNCHRONIZER_case_1(dut: SYNCHRONIZER, trace: lib.Waveform):
    # Inicializa com 0
    dut.async_in.value = BinaryValue('0')
    await trace.cycle()
    await trace.cycle()
    yield trace.check(dut.sync_out, "0", "sync_out deve ser 0 inicialmente")

    # Muda para 1 e espera dois ciclos
    dut.async_in.value = BinaryValue('1')
    await trace.cycle()
    await trace.cycle()
    yield trace.check(dut.sync_out, "1", "sync_out deve virar 1 após 2 ciclos")

    # Volta para 0 e espera dois ciclos
    dut.async_in.value = BinaryValue('0')
    await trace.cycle()
    await trace.cycle()
    yield trace.check(dut.sync_out, "0", "sync_out deve voltar para 0 após 2 ciclos")


@SYNCHRONIZER.testcase
async def tb_SYNCHRONIZER_coverage(dut: SYNCHRONIZER, trace: lib.Waveform):
    trace.disable()

    async_history = []

    for i in range(100):
        await trace.cycle()  # Espera o ciclo ocorrer antes de aplicar nova entrada

        val = str(random.getrandbits(1))
        dut.async_in.value = BinaryValue(val)
        async_history.append(val)

        if i >= 2:
            expected = async_history[i - 2]
            yield trace.check(
                dut.sync_out,
                expected,
                f"Ciclo {i}: async_in={val}, esperado sync_out={expected}"
            )




# Teste de síntese – opcional, para gerar artefatos de VHDL
@pytest.mark.synthesis
def test_SYNCHRONIZER_synthesis():
    SYNCHRONIZER.build_vhd()


# Executa o teste básico
@pytest.mark.testcases
def test_SYNCHRONIZER_testcases():
    SYNCHRONIZER.test_with(tb_SYNCHRONIZER_case_1)


# Executa o teste de estresse
@pytest.mark.coverage
def test_SYNCHRONIZER_stress():
    SYNCHRONIZER.test_with(tb_SYNCHRONIZER_coverage)


# Execução direta com `python test_SYNCHRONIZER.py`
if __name__ == "__main__":
    lib.run_test(__file__)
