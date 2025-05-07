library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity generic_peripheral is
    generic (
        DATA_WIDTH           : natural := 32; -- Data width (CPU bus width)
        OPERATION_CODE_WIDTH : natural := 8 -- Operation code width (Limited to 32 bits)
    );
    port (
        clk         : in  std_logic;
        reset       : in  std_logic;
        wr          : in  std_logic;  -- Write enable signal
        rd          : in  std_logic;  -- Read enable signal
        opcode      : in  std_logic_vector(OPERATION_CODE_WIDTH-1 downto 0); -- Operation code for the peripheral
        data_i      : in  std_logic_vector(DATA_WIDTH-1 downto 0); -- Data input bus (used when writing to the peripheral).
        data_o      : out std_logic_vector(DATA_WIDTH-1 downto 0); -- Data output bus (used when reading from the peripheral).
        interrupt_o : out std_logic -- Interrupt signal to the CPU.
    );
end entity generic_peripheral;

architecture Behavioral of generic_peripheral is
begin
    -- This process demonstrates a simple behavior:
    process(clk, reset)
    begin
        if reset = '1' then
            data_o      <= (others => '0');
            interrupt_o <= '0';
        elsif rising_edge(clk) then
            if unsigned(opcode) = 1 then
                interrupt_o <= '1';
                data_o      <= (others => '1');
            else
                interrupt_o <= '0';
                data_o      <= (others => '0');
            end if;
        end if;
    end process;
end architecture Behavioral;
