library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity generic_register is
    generic (
        WIDTH : integer := 8
    );
    port (
        clk    : in  std_logic;
        reset  : in  std_logic;
        wr_i   : in  std_logic;
        data_i : in  std_logic_vector(WIDTH-1 downto 0);
        data_o : out std_logic_vector(WIDTH-1 downto 0)
    );
end entity generic_register;

architecture Behavioral of generic_register is
    signal reg : std_logic_vector(WIDTH-1 downto 0) := (others => '0');
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if reset = '1' then
                reg <= (others => '0');
            elsif wr_i = '1' then
                reg <= data_i;
            end if;
        end if;
    end process;
    data_o <= reg;
end architecture Behavioral;