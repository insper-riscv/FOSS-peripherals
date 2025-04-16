library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;


entity GENERIC_TRISTATE_BUFFER_1BIT is
    port (
        --! Data Input
        data_in  : in std_logic;
        --! Enable Signal
        enable   : in  std_logic:= '0';
        --! Data Output
        data_out : inout std_logic
    );

end GENERIC_TRISTATE_BUFFER_1BIT;

architecture RTL of GENERIC_TRISTATE_BUFFER_1BIT is
begin
    --! When enable is '1', data_out is equal to data_in. Otherwise, data_out is 'Z'.
    data_out <= data_in when enable = '1' else 'Z';
end architecture;