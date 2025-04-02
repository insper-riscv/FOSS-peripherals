library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library WORK;
entity GENERIC_TRISTATE_BUFFER is
    generic (
        --! Largura dos vetores de dados
        DATA_WIDTH : integer := 8
    );
    port (
        --! Vetor de dados de Entrada
        data_in  : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! Flag de Habilita
        enable   : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! Vetor de dados de Saída
        data_out : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0)
    );
end GENERIC_TRISTATE_BUFFER;
architecture RTL of GENERIC_TRISTATE_BUFFER is
begin
    GEN_TRISTATE : for i in 0 to DATA_WIDTH-1 generate
        BUFFER_INSTANCE : entity WORK.GENERIC_TRISTATE_BUFFER_1BIT
            port map (
                data_in  => data_in(i),
                enable   => enable(i),
                data_out => data_out(i)
            );
    end generate GEN_TRISTATE;
end architecture;