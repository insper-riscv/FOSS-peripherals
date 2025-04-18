-- =============================================================================
-- Entity: GENERIC_SYNCHRONIZER
-- Description: Parameterizable N-stage synchronizer for multi-bit asynchronous
--              inputs. Typically used to reduce metastability risk when
--              transferring signals across clock domains.
-- =============================================================================

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- -----------------------------------------------------------------------------
-- Entity Declaration
-- -----------------------------------------------------------------------------
entity GENERIC_SYNCHRONIZER is
    generic (
        -- Width of the data bus to synchronize
        DATA_WIDTH : natural := 32;
        -- Number of synchronization stages (typically 2 or 3)
        N : natural := 2
    );
    port (
        -- System clock (receiving domain)
        clock     : in  std_logic;
        -- Asynchronous input signal from a different clock domain
        async_in  : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        -- Output signal synchronized to the 'clock' domain
        sync_out  : out std_logic_vector(DATA_WIDTH - 1 downto 0)
    );
end entity GENERIC_SYNCHRONIZER;

-- -----------------------------------------------------------------------------
-- Architecture Definition
-- -----------------------------------------------------------------------------
architecture RTL of GENERIC_SYNCHRONIZER is

    -- Array type to represent the pipeline of synchronization stages
    type sync_array_t is array (0 to N) of std_logic_vector(DATA_WIDTH - 1 downto 0);

    -- Signal that holds all intermediate synchronization stages
    signal sync_stages : sync_array_t;

begin

    -- -----------------------------------------------------------------------------
    -- Stage 0: Assign asynchronous input to first stage in the pipeline
    -- -----------------------------------------------------------------------------
    sync_stages(0) <= async_in;

    -- -----------------------------------------------------------------------------
    -- Stages 1 to N: Pipeline stages implemented using generic registers
    -- -----------------------------------------------------------------------------
    gen_stages : for i in 1 to N generate
        stage_i : entity work.GENERIC_REGISTER
            generic map (
                WIDTH => DATA_WIDTH
            )
            port map (
                clock       => clock,
                clear       => '0',              -- No clear/reset
                enable      => '1',              -- Always enabled
                source      => sync_stages(i - 1), -- Data from previous stage
                destination => sync_stages(i)      -- Output to current stage
            );
    end generate;

    -- -----------------------------------------------------------------------------
    -- Output: Assign last stage in the pipeline to the synchronized output
    -- -----------------------------------------------------------------------------
    sync_out <= sync_stages(N);

end architecture RTL;
