import lib
from peripherals.UARTS.UART_V2.tests.test_GENERIC_FIFO_package import GENERIC_FIFO

class GENERIC_UART_TX(lib.Package):
    pass

class GENERIC_UART_TX_FIFO(lib.Package):
    children = [
        GENERIC_FIFO,
        GENERIC_UART_TX,
    ] 