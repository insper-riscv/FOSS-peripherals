library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.types.all;

entity generic_operation_decoder is
    generic (
        --! Width of the operation bus
        OP_WIDTH               : natural;
        
        --! Width of the control signal
        CONTROL_SIGNAL_WIDTH   : natural;
        
        --! Number of operation-control signal mappings
        MAPPING_NUM            : natural;
        
        --! Matrix that maps operations to control signals
        --! First column: operation, Second column: control signal
        OP_TO_CONTROL_MAP      : operation_mapping_matrix(0 to MAPPING_NUM-1, 0 to 1) := (others => (others => (others => '0')));

        --! Default value for the control signal
        DEFAULT_CONTROL_SIGNAL : std_logic_vector(CONTROL_SIGNAL_WIDTH downto 0) := (others => '0')
    );
    port ( 
        --! Operation to decode
        operation              : in std_logic_vector(OP_WIDTH downto 0);
        
        --! Control signal
        control_signal         : out std_logic_vector(CONTROL_SIGNAL_WIDTH downto 0)
    );
end entity;

architecture Behavioral of generic_operation_decoder is
begin
    -- Process to decode the operation
    decode_proc: process(operation)
        variable match_found : boolean := false;
    begin
        -- Default: set to the default control signal
        control_signal <= DEFAULT_CONTROL_SIGNAL;
        match_found := false;
        
        -- Check if operation matches any of the defined operations
        for i in 0 to MAPPING_NUM-1 loop
            -- If this is the right operation, output the corresponding control signal
            if operation = OP_TO_CONTROL_MAP(i, 0)(OP_WIDTH downto 0) then
                control_signal <= OP_TO_CONTROL_MAP(i, 1)(CONTROL_SIGNAL_WIDTH downto 0);
                match_found := true;
                exit;
            end if;
        end loop;
        
        -- If no match was found, output will remain at the default value
    end process decode_proc;
end architecture Behavioral;