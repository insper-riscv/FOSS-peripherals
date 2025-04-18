-- =============================================================================
-- Entity: Generic_Register
-- Description: Generic Register with synchronous clear and write-enable.
--              Stores input data on rising clock edge when enabled.
-- =============================================================================

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

-- -----------------------------------------------------------------------------
-- Entity Declaration
-- -----------------------------------------------------------------------------
entity Generic_Register is
    generic (
        -- Data bus width
        WIDTH : integer := 8
    );
    port (
        -- Clock signal
        clock       : in  std_logic;
        -- Synchronous clear signal (active high)
        clear       : in  std_logic;
        -- Enable signal for writing data
        enable      : in  std_logic;
        -- Input data bus
        source      : in  std_logic_vector(WIDTH-1 downto 0);
        -- Output data bus
        destination : out std_logic_vector(WIDTH-1 downto 0)
    );
end entity Generic_Register;

-- -----------------------------------------------------------------------------
-- Architecture Definition
-- -----------------------------------------------------------------------------
architecture Behavioral of Generic_Register is
    -- Internal register to hold data
    signal reg : std_logic_vector(WIDTH-1 downto 0) := (others => '0');
begin

    -- Synchronous process triggered on rising clock edge
    process(clock)
    begin
        if rising_edge(clock) then
            -- Clear the register to zero if clear is active
            if clear = '1' then
                reg <= (others => '0');
            -- Load data from source if enabled
            elsif enable = '1' then
                reg <= source;
            end if;
        end if;
    end process;

    -- Drive output with register value
    destination <= reg;

end architecture Behavioral;
