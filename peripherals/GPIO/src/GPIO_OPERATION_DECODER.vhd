library ieee;
use ieee.std_logic_1164.all;

library WORK;

entity GPIO_OPERATION_DECODER is
  port ( 
        --! Address of the GPIO
        address : in std_logic_vector(2 downto 0);
        --! Write Signal
        write       : in  std_logic; 
        --! Read Signal
        read        : in  std_logic; 
        --! Data Decoded
        data_out : out std_logic_vector(7 downto 0)
    );
end entity;

architecture RTL of GPIO_OPERATION_DECODER is
begin
    --! For possible future implementations
    data_out(7) <= '0';
    data_out(6) <= '0';
    --! Read Pin
    data_out(5) <= '1' when (address = "101") AND read else '0';
    --! Read Output
    data_out(4) <= '1' when (address = "100") AND read else '0';
    --! Toggle Output
    data_out(3) <= '1' when (address = "011") AND write else '0';
    --! Write Output
    data_out(2) <= '1' when (address = "010") AND write else '0';
    --! Read Direction
    data_out(1) <= '1' when (address = "001") AND read else '0';
    --! Write Direction
    data_out(0) <= '1' when (address = "000") AND write else '0'; 
end architecture;