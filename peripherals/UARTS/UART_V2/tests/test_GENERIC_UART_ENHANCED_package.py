import lib
from peripherals.UARTS.UART_V2.tests.test_GENERIC_FIFO_package import GENERIC_FIFO

class GENERIC_BAUD_GENERATOR_ENHANCED(lib.Package):
    pass

class GENERIC_UART_TX(lib.Package):
    pass

class GENERIC_UART_RX(lib.Package):
    pass

class GENERIC_UART_TX_FIFO(lib.Package):
    children = [
        GENERIC_FIFO,
        GENERIC_UART_TX,
    ]

class GENERIC_UART_RX_FIFO(lib.Package):
    children = [
        GENERIC_FIFO,
        GENERIC_UART_RX,
    ]

class GENERIC_REGISTER(lib.Package):
    pass

class GENERIC_OPERATION_DECODER(lib.Package):
    pass

class TYPES(lib.Package):
    pass

class GENERIC_UART_ENHANCED(lib.Package):
    children = [
        TYPES,
        GENERIC_FIFO,
        GENERIC_OPERATION_DECODER,
        GENERIC_REGISTER,
        GENERIC_UART_TX,
        GENERIC_UART_RX,
        GENERIC_BAUD_GENERATOR_ENHANCED,
        GENERIC_UART_TX_FIFO,
        GENERIC_UART_RX_FIFO,
    ] 