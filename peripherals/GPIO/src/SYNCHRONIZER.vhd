library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library work;
use work.GENERICS.all;

entity SYNCHRONIZER is
    port (
        --! Processors Clock
        clock    : in  std_logic;
        --! Async Data Input
        async_in : in  std_logic;
        --! Synchronized Data Output
        sync_out : out std_logic
    );
end entity;

architecture RTL of SYNCHRONIZER is
    signal stage1, stage2 : std_logic;
begin
    -- First flip-flop
    FF1 : entity work.GENERIC_FLIP_FLOP
        port map (
            clock  => clock,
            clear  => '0',    -- Clear is always inactive
            enable => '1',    -- Always enabled for synchronization
            source => async_in,
            state  => stage1
        );

    -- Second flip-flop
    FF2 : entity work.GENERIC_FLIP_FLOP 
        port map (
            clock  => clock,
            clear  => '0',    -- Clear is always inactive
            enable => '1',    -- Always enabled for synchronization
            source => stage1,
            state  => stage2
        );

    -- Final synchronized output
    sync_out <= stage2;

end architecture;

