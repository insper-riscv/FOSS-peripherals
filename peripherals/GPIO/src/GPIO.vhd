library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;


entity GPIO is
    generic (
        --! Largura dos vetores de dados
        DATA_WIDTH : integer := 32;
        ADDRESS_WIDTH : integer := 4
    );
    port (
        --! Clock do Processador
        clock       : in  std_logic;
        --! Reset Sincrono dos Registradores
        clear       : in  std_logic; 
        --! Vetor de dados de Entrada
        data_in     : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! Endereço da GPIO a ser acessado
        address     : in  STD_LOGIC_VECTOR(ADDRESS_WIDTH-1 downto 0);
        --! Vetor de dados de Saída
        data_out    : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! Pinos da GPIO
        gpio_pins   : inout std_logic_vector(DATA_WIDTH-1 downto 0)
    );

end GPIO;

architecture RTL of GPIO is

begin
   
end architecture;
