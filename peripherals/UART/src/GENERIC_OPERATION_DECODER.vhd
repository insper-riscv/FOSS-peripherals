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
        DEFAULT_CONTROL_SIGNAL : std_logic_vector(CONTROL_SIGNAL_WIDTH-1 downto 0) := (others => '0')
    );
    port ( 
        --! Operation to decode
        operation              : in std_logic_vector(OP_WIDTH-1 downto 0);
        
        --! Control signal
        control_signal         : out std_logic_vector(CONTROL_SIGNAL_WIDTH-1 downto 0)
    );
end entity;

architecture Behavioral of generic_operation_decoder is
begin
    decode_proc: process(operation)
    begin
        -- start with default
        control_signal <= DEFAULT_CONTROL_SIGNAL;

        -- override if we find a match
        for i in 0 to MAPPING_NUM-1 loop
            if operation = OP_TO_CONTROL_MAP(i, 0) then
                control_signal <= OP_TO_CONTROL_MAP(i, 1);
                exit;
            end if;
        end loop;
    end process decode_proc;
end architecture Behavioral;