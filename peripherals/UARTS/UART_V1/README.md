# UART Version 1 (Original Implementation)

## Overview

This directory contains the original UART implementation with basic functionality:

- **Single-byte operation**: TX and RX handle one byte at a time
- **Simple baud rate generator**: Integer-only divisor
- **Basic interrupts**: Single interrupt signal for all conditions
- **Standard UART protocol**: 8N1 format with even parity

## Features

- ✅ Basic TX/RX functionality
- ✅ Configurable baud rates (integer divisors only)
- ✅ Even parity support
- ✅ Simple interrupt signaling
- ✅ Operation decoder for command interface

## File Structure

```
UART_V1/
├── src/
│   ├── GENERIC_UART.vhd                    # Main UART entity
│   ├── GENERIC_UART_TX.vhd                 # Transmitter
│   ├── GENERIC_UART_RX.vhd                 # Receiver
│   ├── GENERIC_BAUD_GENERATOR.vhd          # Basic baud generator
│   ├── GENERIC_REGISTER.vhd                # Register component
│   ├── GENERIC_OPERATION_DECODER.vhd       # Command decoder
│   ├── GENERIC_OPERATION_DECODER_WRAPPER.vhd
│   └── TYPES.vhd                           # Type definitions
├── tests/
│   ├── test_GENERIC_UART.py                # Main UART tests
│   ├── test_GENERIC_UART_package.py        # Package definition
│   ├── test_GENERIC_BAUD_GENERATOR.py      # Baud generator tests
│   ├── test_GENERIC_UART_TX.py             # TX tests
│   ├── test_GENERIC_UART_RX.py             # RX tests
│   └── [other test files...]
└── README.md                               # This file
```

## Usage

This is the stable, proven implementation suitable for:
- Low-throughput applications
- Simple UART communication needs
- Educational purposes
- Legacy system compatibility

## Testing

Run the tests from the UART_V1 directory:

```bash
# Change to UART V1 directory  
cd peripherals/UARTS/UART_V1

# Test the original UART implementation
python3 -m pytest tests/ -v
```

## Migration

For high-performance applications, consider upgrading to **UART_V2** which provides:
- FIFO buffers for improved throughput
- Fractional baud rate generators for better accuracy
- Enhanced error detection
- Separate interrupt signals

See `../UART_V2/` for the enhanced implementation. 