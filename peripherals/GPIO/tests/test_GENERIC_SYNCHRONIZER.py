import random
import pytest
from cocotb.binary import BinaryValue

import lib


class GENERIC_SYNCHRONIZER(lib.Entity):
    """
    Maps to VHDL entity GENERIC_SYNCHRONIZER, which
    has a 32-bit async_in by default.
    """
    clock    = lib.Entity.Input_pin
    async_in = lib.Entity.Input_pin
    sync_out = lib.Entity.Output_pin


@GENERIC_SYNCHRONIZER.testcase
async def tb_SYNCHRONIZER_case_1(dut, trace):
    """
    Teste básico para o sincronizador de 32 bits usando padrões fixos (máscaras).
    """
    N = int(dut.N)
    dut._log.info(f"Teste Manual Synchronizer com N = {N} (DATA_WIDTH=32)")

    # Máscaras como strings de 32 bits
    MASKS = {
        "todos zeros":     '0' * 32,
        "todos uns":       '1' * 32,
        "alternando 1010": ''.join(['10' for _ in range(16)]),  # 0xAAAAAAAA
        "alternando 0101": ''.join(['01' for _ in range(16)]),  # 0x55555555
        "metade alta":     '1' * 16 + '0' * 16,                 # 0xFFFF0000
        "metade baixa":    '0' * 16 + '1' * 16,                 # 0x0000FFFF
        "padrão central":  '00000000111111110000000011111111'   # 0x00FF00FF
    }

    for nome, binstr in MASKS.items():
        dut._log.info(f"Aplicando padrão: {nome} -> {binstr}")
        dut.async_in.value = BinaryValue(binstr)
        for _ in range(N):
            await trace.cycle()
        yield trace.check(
            dut.sync_out,
            binstr,
            f"sync_out deve ser {binstr} ({nome}) após {N} ciclos"
        )

    dut._log.info("Teste básico com todas as máscaras finalizado com sucesso.")



@GENERIC_SYNCHRONIZER.testcase
async def tb_SYNCHRONIZER_stress(dut, trace):
    """
    Random test for 32-bit wide async_in.
    We generate random 32-bit values and confirm
    they appear on sync_out after N cycles.
    """
    trace.disable()
    N = int(dut.N)
    dut._log.info(f"Teste de estresse para SYNCHRONIZER (32 bits) com N={N}")

    in_history = []
    NUM_CYCLES = 50

    for i in range(NUM_CYCLES):
        await trace.cycle()
        # Generate a random 32-bit integer
        val_int = random.getrandbits(32)
        # Convert to a 32-bit binary string
        val_str = f"{val_int:032b}"

        # Assign it to the input
        dut.async_in.value = BinaryValue(val_str)
        in_history.append(val_str)

        # Check output once we have at least N pipeline cycles
        if i >= N:
            expected = in_history[i - N]
            yield trace.check(
                dut.sync_out,
                expected,
                f"Ciclo {i}: esperado={expected}, obtido={dut.sync_out.value}"
            )

    dut._log.info("Teste de estresse finalizado com sucesso.")


@pytest.mark.synthesis
def test_SYNCHRONIZER_synthesis():
    """Optional: generate VHDL synthesis artifacts."""
    GENERIC_SYNCHRONIZER.build_vhd()


@pytest.mark.testcases
def test_SYNCHRONIZER_testcases():
    """Rodar o teste básico para N=2 e N=4."""
    GENERIC_SYNCHRONIZER.test_with(tb_SYNCHRONIZER_case_1, {"N": 2})
    GENERIC_SYNCHRONIZER.test_with(tb_SYNCHRONIZER_case_1, {"N": 4})


@pytest.mark.coverage
def test_SYNCHRONIZER_coverage():
    """Rodar o teste de estresse para N=2 e N=4."""
    GENERIC_SYNCHRONIZER.test_with(tb_SYNCHRONIZER_stress, {"N": 2})
    GENERIC_SYNCHRONIZER.test_with(tb_SYNCHRONIZER_stress, {"N": 4})


if __name__ == "__main__":
    lib.run_test(__file__)
