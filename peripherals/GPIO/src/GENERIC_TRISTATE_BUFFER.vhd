-- =============================================================================
-- Entity: GENERIC_TRISTATE_BUFFER
-- Description: Parameterizable N-bit tri-state buffer.
--              Uses a 1-bit tri-state buffer instance per bit, controlled by 
--              per-bit enable lines. When enabled, each bit of data_in is 
--              driven onto data_out; otherwise, data_out is 'Z' (high-impedance).
-- =============================================================================

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;

-- -----------------------------------------------------------------------------
-- Entity Declaration
-- -----------------------------------------------------------------------------
entity GENERIC_TRISTATE_BUFFER is
    generic (
        -- Width of the data bus
        DATA_WIDTH : integer := 8
    );
    port (
        -- Input data vector to drive onto the bus
        data_in  : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        -- Enable flags for each bit (1 = drive, 0 = high-impedance)
        enable   : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        -- Output bus driven by individual tri-state buffers
        data_out : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0)
    );
end entity GENERIC_TRISTATE_BUFFER;

-- -----------------------------------------------------------------------------
-- Architecture Definition
-- -----------------------------------------------------------------------------
architecture RTL of GENERIC_TRISTATE_BUFFER is
begin

    -- Generate a tri-state buffer instance for each bit of the vector
    GEN_TRISTATE : for i in 0 to DATA_WIDTH-1 generate
        BUFFER_INSTANCE : entity WORK.GENERIC_TRISTATE_BUFFER_1BIT
            port map (
                data_in  => data_in(i),
                enable   => enable(i),
                data_out => data_out(i)
            );
    end generate GEN_TRISTATE;

end architecture;
