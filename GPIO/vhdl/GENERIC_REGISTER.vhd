library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;

--! Registrador de uso geral
entity GENERIC_REGISTER is

    generic (
        --! Largura dos vetores de dados
        DATA_WIDTH : natural := 8
    );

    port (
        --! Sinal de clock
        clock       : in  std_logic;
        --! Sinal de clear
        clear       : in  std_logic := '1';
        --! Habilita a entidade
        enable      : in  std_logic := 'X';
        --! Vetor de dados para escrita
        source      : in  std_logic_vector((DATA_WIDTH - 1) downto 0) := (others => 'X');
        --! Vetor de dados regisrados
        destination : out std_logic_vector((DATA_WIDTH - 1) downto 0) := (others => '0')
    );

end entity;

architecture RTL of GENERIC_REGISTER is

    -- No signals

begin

    --! Durante a borda de subida de `clock`, caso `enable` esteja habilitado,
    --! atribui `source` a `destination` se `clear` nãoestiver habilitado, caso
    --! contrário atribui vetor booleano baixo a `destination`.
    UPDATE : process(clock)
    begin
        if (rising_edge(clock)) then
            if (enable = '1') then
                if (clear = '1') then
                    destination <= (others => '0');
                else
                    destination <= source;
                end if;
            end if;
        end if;
    end process;

end architecture;