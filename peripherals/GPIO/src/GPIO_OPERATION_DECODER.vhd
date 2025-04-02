library ieee;
use ieee.std_logic_1164.all;

library WORK;

entity GPIO_OPERATION_DECODER is
  port ( 
        --! Address of the GPIO
        address : in std_logic_vector(3 downto 0);
        --! Enable direction register
        dir_enable : out std_logic;
        --! Write Operation Selector
        write_op : out std_logic_vector(1 downto 0);
        --! Read Operation Selector
        read_op : out std_logic_vector(1 downto 0)
    );
end entity;

architecture RTL of GPIO_OPERATION_DECODER is
begin
    --! Memory 0x00 to 0x04 assigns the signal for writing operations
    dir_enable <= '1' when (address = "0000") else '0';
    write_op <= "00" when (address = "0001") else
                "01" when (address = "0010") else
                "10" when (address = "0011") else
                "11" when (address = "0100") else
                "00";
    --! Memory 0x05 to 0x07 assigns the signal for reading operations
    read_op <= "00" when (address = "0101") else
                "01" when (address = "0110") else
                "10" when (address = "0111") else
                "11";
    --! Else No Operation
end architecture;