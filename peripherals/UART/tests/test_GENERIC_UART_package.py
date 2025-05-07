import pytest
import lib
from peripherals.UART.tests.test_TYPES_package import TYPES
from peripherals.UART.tests.test_GENERIC_OPERATION_DECODER_package import GENERIC_OPERATION_DECODER

class GENERIC_BAUD_GENERATOR(lib.Package):
    pass

class GENERIC_UART_TX(lib.Package):
    pass

class GENERIC_UART_RX(lib.Package):
    pass

class GENERIC_REGISTER(lib.Package):
    pass

class GENERIC_UART(lib.Package):
    children = [
        TYPES,
        GENERIC_OPERATION_DECODER,
        GENERIC_BAUD_GENERATOR,
        GENERIC_UART_TX,
        GENERIC_UART_RX,
        GENERIC_REGISTER,
    ]

@pytest.mark.synthesis
def test_GENERIC_UART_TB_package_synthesis():
    GENERIC_UART.build_vhd()

if __name__ == "__main__":
    lib.run_test(__file__)