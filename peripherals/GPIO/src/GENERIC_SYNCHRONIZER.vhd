library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity GENERIC_SYNCHRONIZER is
    generic (
        DATA_WIDTH : natural := 32;
        N : natural := 2
    );
    port (
        --! System clock
        clock     : in  std_logic;
        --! Asynchronous data input
        async_in  : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        --! Synchronized data output
        sync_out  : out std_logic_vector(DATA_WIDTH - 1 downto 0)
    );
end entity GENERIC_SYNCHRONIZER;

architecture RTL of GENERIC_SYNCHRONIZER is

    --! Declare an array type to hold the data for each stage of the synchronizer.
    type sync_array_t is array (0 to N) of std_logic_vector(DATA_WIDTH-1 downto 0);

    --! Create a signal of the array type to hold the pipeline data.
    signal sync_stages : sync_array_t;

begin
    --! 1) Assign the external async input to the first entry in the array.
    sync_stages(0) <= async_in;

    --! 2) Generate multiple register stages (i in [1..N]).
    gen_stages : for i in 1 to N generate
        stage_i : entity work.GENERIC_REGISTER
            generic map (
                DATA_WIDTH => DATA_WIDTH
            )
            port map (
                clock       => clock,
                clear       => '0',              -- No clear (tie low)
                enable      => '1',              -- Always enabled
                source      => sync_stages(i-1), -- Input from previous stage
                destination => sync_stages(i)    -- Output to this stage
            );
    end generate;

    --! 3) The synchronized output is the last entry of the array (index = N).
    sync_out <= sync_stages(N);

end architecture RTL;
