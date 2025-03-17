library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;


entity GENERIC_TRISTATE_BUFFER_1BIT is
    port (
        --! Vetor de dados de Entrada
        data_in  : in std_logic;
        --! Flag de Habilita
        enable   : in  std_logic:= '0';
        --! Vetor de dados de Saída
        data_out : inout std_logic
    );

end GENERIC_TRISTATE_BUFFER_1BIT;

architecture RTL of GENERIC_TRISTATE_BUFFER_1BIT is
begin
    -- Funciona como multiplexador. Caso enable seja 0 a data_out <= data_in. Caso contrário recebe alta impedância.
    data_out <= data_in when enable = '1' else 'Z';
end architecture;