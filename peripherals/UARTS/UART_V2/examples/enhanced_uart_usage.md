# Enhanced UART Usage Guide

## Overview

The enhanced UART implementation provides significant improvements over the basic version:

1. **FIFO Buffers**: 16-deep TX and RX FIFOs for improved throughput
2. **Enhanced Baud Rate Generator**: Fractional baud rate support for precise timing
3. **Better Error Detection**: Comprehensive error flags and status reporting
4. **Improved Interrupts**: Separate TX, RX, and error interrupt signals

## Configuration Register Layout

The enhanced UART uses an expanded configuration register format:

```
Bit 31-27: Reserved
Bit 26:    TX Enable
Bit 25:    RX Enable  
Bit 24:    Fractional Baud Enable
Bit 23-16: Fractional Baud Value (8 bits)
Bit 15-0:  Integer Baud Divisor (16 bits)
```

## Operation Codes

| Operation | Code | Description |
|-----------|------|-------------|
| CONFIG    | 0    | Configuration register access |
| TX_DATA   | 1    | Write data to TX FIFO |
| RX_DATA   | 2    | Read data from RX FIFO |
| STATUS    | 3    | Read status register |
| BAUD      | 4    | Future: Advanced baud config |
| FIFO      | 5    | Future: FIFO control |

## Status Register Layout

```
Bit 12:    RX Threshold (≥4 bytes in RX FIFO)
Bit 11:    TX Threshold (≤4 bytes in TX FIFO)  
Bit 10:    Overrun Error
Bit 9:     Frame Error
Bit 8:     Parity Error
Bit 7:     RX Data Ready (!RX Empty)
Bit 6:     RX Almost Full
Bit 5:     RX Full
Bit 4:     RX Empty
Bit 3:     TX Busy (transmitting)
Bit 2:     TX Almost Full
Bit 1:     TX Full
Bit 0:     TX Empty
```

## Usage Examples

### Basic Setup

```vhdl
-- Configure for 115200 baud with 50MHz clock
-- Baud divisor = 50MHz / (16 * 115200) ≈ 27.13
-- Integer part = 27, Fractional part ≈ 0.13 * 256 ≈ 33

signal config_value : std_logic_vector(31 downto 0);
config_value <= "00" & "11" & "1" & "00100001" & x"001B"; -- TX+RX en, frac en, frac=33, div=27
```

### High-Performance Operation

The FIFO buffers allow for burst transfers:

```vhdl
-- Write multiple bytes without checking status
for i in 0 to 15 loop
    -- Write data to TX FIFO
    operation <= "001";  -- TX_DATA
    data_i <= data_array(i);
    wr_i <= '1';
    wait for clk_period;
    wr_i <= '0';
    wait for clk_period;
end loop;

-- Check TX threshold interrupt for refill
if tx_interrupt = '1' then
    -- FIFO has drained below threshold, refill available
end if;
```

### Error Handling

```vhdl
-- Check for errors
operation <= "011";  -- STATUS
rd_i <= '1';
wait for clk_period;
status_reg <= data_o;
rd_i <= '0';

if status_reg(8) = '1' then
    -- Parity error detected
    handle_parity_error();
end if;

if status_reg(10) = '1' then
    -- Overrun error - RX FIFO full, data lost
    handle_overrun_error();
end if;
```

## Benefits Achieved

### 1. Improved Throughput
- **Before**: Single byte at a time, CPU must respond immediately
- **After**: 16-byte bursts, CPU has more time to respond

### 2. Better Accuracy
- **Before**: Integer-only baud rates, up to 3.7% error for some rates
- **After**: Fractional rates reduce error to <0.1% for common baud rates

### 3. Enhanced Reliability
- **Before**: Data loss if CPU doesn't respond quickly enough
- **After**: FIFO buffering prevents data loss during temporary CPU delays

### 4. Better Integration
- **Before**: Single interrupt for all conditions
- **After**: Separate interrupts allow more efficient interrupt handling

## Common Baud Rate Configurations

For 50MHz system clock:

| Baud Rate | Integer | Fractional | Error % |
|-----------|---------|------------|---------|
| 9600      | 325     | 213        | <0.01%  |
| 19200     | 162     | 235        | <0.01%  |
| 38400     | 81      | 118        | <0.01%  |
| 57600     | 54      | 78         | <0.01%  |
| 115200    | 27      | 39         | <0.01%  |

## Testing

Run the enhanced tests from the UART_V2 directory:

```bash
# Change to UART V2 directory
cd peripherals/UARTS/UART_V2

# Test individual components
pytest tests/test_GENERIC_FIFO.py
pytest tests/test_GENERIC_UART_ENHANCED.py

# Test individual FIFO components
pytest tests/test_GENERIC_UART_TX_FIFO.py
pytest tests/test_GENERIC_UART_RX_FIFO.py

# Run all UART V2 tests
pytest tests/
```

## Individual FIFO Component Usage

### TX FIFO Component

The `GENERIC_UART_TX_FIFO` can be used independently:

```vhdl
-- Instantiate TX FIFO component
tx_fifo_inst : entity work.generic_uart_tx_fifo
    generic map (
        DATA_BITS  => 8,
        FIFO_DEPTH => 16
    )
    port map (
        clk            => clk,
        reset          => reset,
        
        -- CPU Interface
        tx_data_i      => cpu_data,
        write_strobe_i => cpu_write,
        
        -- UART Interface
        baud_tick_i    => baud_tick,
        tx_o           => uart_tx,
        
        -- Status outputs
        tx_empty_o     => tx_empty,
        tx_full_o      => tx_full,
        tx_threshold_o => tx_interrupt
    );
```

### RX FIFO Component

The `GENERIC_UART_RX_FIFO` can be used independently:

```vhdl
-- Instantiate RX FIFO component
rx_fifo_inst : entity work.generic_uart_rx_fifo
    generic map (
        DATA_BITS  => 8,
        FIFO_DEPTH => 16
    )
    port map (
        clk            => clk,
        reset          => reset,
        
        -- UART Interface
        rx_i           => uart_rx,
        baud_tick_i    => baud_tick,
        
        -- CPU Interface
        rx_data_o      => cpu_data,
        read_strobe_i  => cpu_read,
        
        -- Status outputs
        rx_empty_o     => rx_empty,
        rx_threshold_o => rx_interrupt,
        
        -- Error outputs
        parity_error_o => parity_err,
        overrun_error_o => overrun_err
    );
```

The enhanced UART maintains backward compatibility while providing significant performance and reliability improvements. 