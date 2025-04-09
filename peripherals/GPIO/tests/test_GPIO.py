'''
import pytest
from cocotb.binary import BinaryValue
import lib
import random

from test_GENERICS_package import GENERICS

class GPIO(lib.Entity):
    _package = GENERICS

    clock     = lib.Entity.Input_pin
    clear     = lib.Entity.Input_pin
    data_in   = lib.Entity.Input_pin
    address   = lib.Entity.Input_pin
    write     = lib.Entity.Input_pin
    read      = lib.Entity.Input_pin
    data_out  = lib.Entity.Output_pin
    gpio_pins = lib.Entity.Output_pin  # inout no HDL, tratado como output no testbench

ADDR = {
    "write_dir":     "000",
    "write_out_load":"001",
    "write_out_set": "010",
    "write_out_clear":"011",
    "toggle":        "100",
    "read_dir":      "101",
    "read_out":      "110",
    "read_external": "111"
}

# Função auxiliar para executar operação GPIO
async def gpio_op(dut, trace, op, data_in=None, write=False, read=False):
    dut.address.value = BinaryValue(ADDR[op], n_bits=3)
    dut.write.value = BinaryValue('1' if write else '0')
    dut.read.value  = BinaryValue('1' if read else '0')
    if data_in is not None:
        if isinstance(data_in, int):
            dut.data_in.value = BinaryValue(format(data_in, '032b'))
        else:
            dut.data_in.value = BinaryValue(data_in, n_bits=32)
    await trace.cycle()
    dut.write.value = BinaryValue('0')
    dut.read.value  = BinaryValue('0')

@GPIO.testcase
async def tb_gpio_alternating_patterns(dut: GPIO, trace: lib.Waveform):
    #Edge Case. Checa se pinos e saída estão em alta impedância 
    yield trace.check(dut.data_out, "Z" * 32, "Direção deve estar toda em Z")
    yield trace.check(dut.gpio_pins, "Z" * 32, "Direção deve estar toda em Z")
    dut.clear.value = BinaryValue('1')
    await trace.cycle()
    dut.clear.value = BinaryValue('0')

    # Define direção de todos os bits como saída
    await gpio_op(dut, trace, "write_dir", data_in=0xFFFFFFFF, write=True)

    # Lê direção e verifica se todos os bits estão setados
    await gpio_op(dut, trace, "read_dir", read=True)
    yield trace.check(dut.data_out, "1" * 32, "Direção deve estar toda em 1")

    # Padrão 1: Alternado A (101010...)
    pattern1 = 0xAAAAAAAA
    await gpio_op(dut, trace, "write_out_load", data_in=pattern1, write=True)

    await gpio_op(dut, trace, "read_out", read=True)
    yield trace.check(dut.data_out, format(pattern1, '032b'), "Saída deve conter padrão A (0xAAAAAAAA)")
    yield trace.check(dut.gpio_pins, format(pattern1, '032b'), "GPIO deve refletir padrão A")

    # Toggle: deve inverter todos os bits de padrão1 → padrão2 (010101...)
    await gpio_op(dut, trace, "toggle", data_in=0xFFFFFFFF, write=True)

    expected_toggle = pattern1 ^ 0xFFFFFFFF  # deve ser 0x55555555
    await gpio_op(dut, trace, "read_out", read=True)
    yield trace.check(dut.data_out, format(expected_toggle, '032b'), "Saída deve ter sido invertida (0x55555555)")
    yield trace.check(dut.gpio_pins, format(expected_toggle, '032b'), "GPIO deve refletir padrão invertido")

    # Clear bits com padrão alternado (zera bits 1, 3, 5, ...)
    await gpio_op(dut, trace, "write_out_clear", data_in=0xAAAAAAAA, write=True)

    cleared = expected_toggle & ~0xAAAAAAAA
    await gpio_op(dut, trace, "read_out", read=True)
    yield trace.check(dut.data_out, format(cleared, '032b'), "Saída deve ter bits A zerados")
    yield trace.check(dut.gpio_pins, format(cleared, '032b'), "GPIO deve refletir bits A zerados")

    # Set bits alternados novamente (bits 1, 3, 5, ...)
    await gpio_op(dut, trace, "write_out_set", data_in=0xAAAAAAAA, write=True)

    final = cleared | 0xAAAAAAAA
    await gpio_op(dut, trace, "read_out", read=True)
    yield trace.check(dut.data_out, format(final, '032b'), "Saída deve restaurar padrão A")
    yield trace.check(dut.gpio_pins, format(final, '032b'), "GPIO deve refletir padrão A novamente")


# Teste de estresse com operações aleatórias
@GPIO.testcase
async def tb_gpio_stress(dut: GPIO, trace: lib.Waveform):
    yield trace.check(dut.data_out, "Z" * 32, "Direção deve estar toda em Z")
    yield trace.check(dut.gpio_pins, "Z" * 32, "Direção deve estar toda em Z")
    dut.clear.value = BinaryValue('1')
    await trace.cycle()
    dut.clear.value = BinaryValue('0')

    await gpio_op(dut, trace, "write_dir", data_in=0xFFFFFFFF, write=True)

    expected_value = 0

    for i in range(100):
        op = random.choice(["write_out_load", "write_out_set", "write_out_clear", "toggle"])
        data = random.getrandbits(32)

        if op == "write_out_load":
            await gpio_op(dut, trace, op, data_in=data, write=True)
            expected_value = data
        elif op == "write_out_set":
            await gpio_op(dut, trace, op, data_in=data, write=True)
            expected_value |= data
        elif op == "write_out_clear":
            await gpio_op(dut, trace, op, data_in=data, write=True)
            expected_value &= ~data & 0xFFFFFFFF
        elif op == "toggle":
            await gpio_op(dut, trace, op, data_in=data, write=True)
            expected_value ^= data

        await gpio_op(dut, trace, "read_out", read=True)
        yield trace.check(
            dut.data_out,
            format(expected_value, '032b'),
            f"[{i}] Esperado data_out = {hex(expected_value)} após {op.upper()}"
        )
        yield trace.check(
            dut.gpio_pins,
            format(expected_value, '032b'),
            f"[{i}] gpio_pins deve ser {hex(expected_value)} após {op.upper()}"
        )

# Síntese
@pytest.mark.synthesis
def test_GPIO_synthesis():
    GPIO.build_vhd()

# Teste fixo
@pytest.mark.testcases
def test_gpio_basic():
    GPIO.test_with(tb_gpio_alternating_patterns)

# Teste estresse
@pytest.mark.coverage
def test_gpio_stress():
    GPIO.test_with(tb_gpio_stress)

if __name__ == "__main__":
    lib.run_test(__file__)'''

import pytest
from cocotb.binary import BinaryValue
import lib
from test_GENERICS_package import GENERICS

# Assuming the same base class for the GPIO
class GPIO(lib.Entity):
    _package = GENERICS

    clock     = lib.Entity.Input_pin
    clear     = lib.Entity.Input_pin
    data_in   = lib.Entity.Input_pin
    address   = lib.Entity.Input_pin
    write     = lib.Entity.Input_pin
    read      = lib.Entity.Input_pin
    data_out  = lib.Entity.Output_pin
    gpio_pins = lib.Entity.Input_pin  


# GPIO Address mapping 
ADDR = {
    "write_dir":     "000",
    "write_out_load":"001",
    "write_out_set": "010",
    "write_out_clear":"011",
    "toggle":        "100",
    "read_dir":      "101",
    "read_out":      "110",
    "read_external": "111",
}


# Helper coroutine to do the operation
async def gpio_op(dut, trace, op, data_in=None, write=False, read=False):
    dut.address.value = BinaryValue(ADDR[op], n_bits=3)
    dut.write.value   = BinaryValue('1' if write else '0')
    dut.read.value    = BinaryValue('1' if read  else '0')

    if data_in is not None:
        # If data_in is int, convert to 32-bit binary string
        if isinstance(data_in, int):
            dut.data_in.value = BinaryValue(format(data_in, '032b'))
        else:
            # If already a string, make sure it's 32 bits
            dut.data_in.value = BinaryValue(data_in, n_bits=32)

    # Wait one cycle, then de-assert
    await trace.cycle()
    dut.write.value = BinaryValue('0')
    dut.read.value  = BinaryValue('0')


# A simple GPIO "read from pins" test
@GPIO.testcase
async def tb_gpio_input_basic(dut: GPIO, trace: lib.Waveform):
    """
    1) Clear the design
    2) Configure direction register = 0 (all inputs)
    3) Drive external pins
    4) Read from 'read_external' address
    5) Check that data_out matches the external pins
    """

    # 1) Clear the design
    dut.clear.value = BinaryValue('1')
    await trace.cycle()
    dut.clear.value = BinaryValue('0')

    # 2) Direction register = 0 -> all input bits
    await gpio_op(dut, trace, "write_dir", data_in=0, write=True)

    # Optional: Check the direction register read-back
    await gpio_op(dut, trace, "read_dir", read=True)
    yield trace.check(
        dut.data_out,
        "0"*32,
        "All bits should be inputs (0 in direction register)."
    )

    # 3) Drive an external value
    external_value = 0xABCD1234
    dut.gpio_pins.value = BinaryValue(format(external_value, '032b'))

    # 4) Read from 'read_external' address
    # The design has a 2-stage synchronizer, so let's wait 2 cycles
    dut.address.value = BinaryValue(ADDR["read_external"], n_bits=3)
    dut.read.value    = BinaryValue('1')
    await trace.cycle()  # first sync stage
    await trace.cycle()  # second sync stage

    # 5) Check data_out
    # By this time, reg_input (the synchronizer output) should match external_value
    yield trace.check(
        dut.data_out,
        format(external_value, '032b'),
        "GPIO input readback should match the external pins."
    )

    # Stop driving read
    dut.read.value = BinaryValue('0')


@pytest.mark.synthesis
def test_GPIO_synthesis():
    GPIO.build_vhd()

@pytest.mark.testcases
def test_input_basic():
    GPIO.test_with(tb_gpio_input_basic)

if __name__ == "__main__":
    lib.run_test(__file__)
