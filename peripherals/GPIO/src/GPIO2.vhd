library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;

entity GPIO is
    generic (
        --! Data Width
        DATA_WIDTH : integer := 32
    );
    port (
        --! Clock Signal
        clock       : in  std_logic;
        --! Clear Signal
        clear       : in  std_logic; 
        --! Data Inputed from the Processor
        data_in     : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! GPIO Address accessed by the Processor
        address     : in  STD_LOGIC_VECTOR(2 downto 0);
        --! Write Signal
        write       : in  std_logic; 
        --! Read Signal
        read        : in  std_logic; 
        --! Data Outputed to the Processor
        data_out    : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! GPIO Pins
        gpio_pins   : inout std_logic_vector(DATA_WIDTH-1 downto 0)
    );
end GPIO;

architecture RTL of GPIO is



begin



end architecture;
