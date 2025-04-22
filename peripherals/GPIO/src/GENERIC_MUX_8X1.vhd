-- =============================================================================
-- Entity: GENERIC_MUX_8X1
-- Description: 8-to-1 multiplexer with parameterizable data width.
--              Selects one of eight input vectors based on a 3-bit selector.
-- =============================================================================

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- -----------------------------------------------------------------------------
-- Entity Declaration
-- -----------------------------------------------------------------------------
entity GENERIC_MUX_8X1 is
    generic (
        -- Width of the data vectors
        DATA_WIDTH : natural := 8
    );
    port (
        selector     : in  std_logic_vector(2 downto 0);
        source_0     : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        source_1     : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        source_2     : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        source_3     : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        source_4     : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        source_5     : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        source_6     : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        source_7     : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        destination  : out std_logic_vector(DATA_WIDTH - 1 downto 0)
    );
end entity;

-- -----------------------------------------------------------------------------
-- Architecture Definition
-- -----------------------------------------------------------------------------
architecture RTL of GENERIC_MUX_8X1 is
begin
    destination <= 
        (source_0 and (others =>     not selector(2) and     not selector(1) and     not selector(0))) or
        (source_1 and (others =>     not selector(2) and     not selector(1) and      selector(0))) or
        (source_2 and (others =>     not selector(2) and      selector(1) and     not selector(0))) or
        (source_3 and (others =>     not selector(2) and      selector(1) and      selector(0))) or
        (source_4 and (others =>      selector(2) and     not selector(1) and     not selector(0))) or
        (source_5 and (others =>      selector(2) and     not selector(1) and      selector(0))) or
        (source_6 and (others =>      selector(2) and      selector(1) and     not selector(0))) or
        (source_7 and (others =>      selector(2) and      selector(1) and      selector(0)));
end architecture;
