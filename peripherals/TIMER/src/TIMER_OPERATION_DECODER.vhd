library ieee;
use ieee.std_logic_1164.all;

library WORK;

entity TIMER_OPERATION_DECODER is
  port (
    -- Address that selects a timer operation
    address          : in  std_logic_vector(3 downto 0);
    -- Control signal from the processor
    write            : in  std_logic;
    -- Decoded outputs for timer control
    start_counter    : out std_logic;
    op_counter       : out std_logic_vector(1 downto 0);
    load_reset_value : out std_logic;
    read_op     : out std_logic
  );
end entity;

architecture RTL of TIMER_OPERATION_DECODER is
begin
    -- Assert start_counter on address 0x00
    start_counter <= '1' when (address = "0000" and write = '1') else '0';
    -- Assert load_reset_value on address 0x01 
    load_reset_value <= '1' when (address = "0001" and write = '1') else '0';
    -- Set counter_op for different counter operations on addresses 0x02, 0x03, 0x04 (Increment, Load, Reset)
    op_counter <="01" when (address = "0010") else
                 "10" when (address = "0011") else
                 "00";

    -- Set read_op for different read operation addresses. Read Overflow: 0x05. Elsewhere, read current value. 
    read_op <= '1' when (address = "0100") else '0';

    -- All other address writes/read => No operation
end architecture;
