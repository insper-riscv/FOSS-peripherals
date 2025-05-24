library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.types.all;

entity generic_operation_decoder is
    generic (
  
        --! Width of the control signal
        CONTROL_SIGNAL_WIDTH           : natural;

        --! Width of the operation
        OP_WIDTH                       : natural;
        
        --! Number of operation-to-control signal mappings
        OPERATION_CONTROL_SIGNAL_COUNT : natural;
        
        --! Matrix that maps operations to control signals
        --! The first column is the operation, the second column is the control signal
        OPERATION_TO_CONTROL_MAP       : op_cs_map(0 to OPERATION_CONTROL_SIGNAL_COUNT-1);

        --! Default value for the control signal
        DEFAULT_CONTROL_SIGNAL         : std_logic_vector(CONTROL_SIGNAL_WIDTH-1 downto 0) := (others => '0')
    );
    port ( 
        --! Operation to decode
        operation                      : in std_logic_vector(OP_WIDTH-1 downto 0);
        
        --! Control signal
        control_signal                 : out std_logic_vector(CONTROL_SIGNAL_WIDTH-1 downto 0)
    );
end entity;

architecture Behavioral of generic_operation_decoder is
begin
    decode_proc: process(operation)
    begin
        control_signal <= DEFAULT_CONTROL_SIGNAL;
        for i in 0 to OPERATION_CONTROL_SIGNAL_COUNT-1 loop
            if operation = OPERATION_TO_CONTROL_MAP(i).op then
                control_signal <= OPERATION_TO_CONTROL_MAP(i).ctrl;
                exit;
            end if;
        end loop;
    end process decode_proc;
end architecture Behavioral;