library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity generic_baud_generator is
    generic (
        COUNTER_WIDTH : natural := 16
    );
    port (
      clk         : in  std_logic;
      reset       : in  std_logic;
      baud_div_i  : in  unsigned(COUNTER_WIDTH-1 downto 0);
      tick        : out std_logic
    );
end entity generic_baud_generator;

architecture Behavioral of generic_baud_generator is
    signal counter : unsigned(COUNTER_WIDTH-1 downto 0) := (others => '0');
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if reset = '1' then
                counter <= (others => '0');
                tick <= '0';
            elsif counter = baud_div_i then
                counter <= (others => '0');
                tick <= '1';
            else
                counter <= counter + 1;
                tick <= '0';
            end if;
        end if;
    end process;
end architecture Behavioral;