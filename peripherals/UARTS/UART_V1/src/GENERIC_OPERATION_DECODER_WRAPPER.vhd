library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.types.all;

entity generic_operation_decoder_wrapper is
    generic (
        OP_WIDTH                       : natural := 3;
        CONTROL_SIGNAL_WIDTH           : natural := 2;
        OPERATION_CONTROL_SIGNAL_COUNT : natural := 4;

        -- Operation values (as integers)
        OP_0 : integer := 0;
        OP_1 : integer := 1;
        OP_2 : integer := 2;
        OP_3 : integer := 3;

        -- Control values (as integers)
        CTRL_0 : integer := 1;
        CTRL_1 : integer := 2;
        CTRL_2 : integer := 3;
        CTRL_3 : integer := 0;

        -- Default control value (as integer)
        DEFAULT_CTRL : integer := 0
    );
    port (
        operation      : in  std_logic_vector(OP_WIDTH-1 downto 0);
        control_signal : out std_logic_vector(CONTROL_SIGNAL_WIDTH-1 downto 0)
    );
end entity;

architecture Behavioral of generic_operation_decoder_wrapper is

    -- Build the mapping as a constant array of op_cs_pair
    constant OPERATION_TO_CONTROL_MAP : op_cs_map(0 to OPERATION_CONTROL_SIGNAL_COUNT-1) := (
        0 => (op   => std_logic_vector(to_unsigned(OP_0, OP_WIDTH)),
              ctrl => std_logic_vector(to_unsigned(CTRL_0, CONTROL_SIGNAL_WIDTH))),
        1 => (op   => std_logic_vector(to_unsigned(OP_1, OP_WIDTH)),
              ctrl => std_logic_vector(to_unsigned(CTRL_1, CONTROL_SIGNAL_WIDTH))),
        2 => (op   => std_logic_vector(to_unsigned(OP_2, OP_WIDTH)),
              ctrl => std_logic_vector(to_unsigned(CTRL_2, CONTROL_SIGNAL_WIDTH))),
        3 => (op   => std_logic_vector(to_unsigned(OP_3, OP_WIDTH)),
              ctrl => std_logic_vector(to_unsigned(CTRL_3, CONTROL_SIGNAL_WIDTH)))
    );

    constant DEFAULT_CONTROL_SIGNAL : std_logic_vector(CONTROL_SIGNAL_WIDTH-1 downto 0) :=
        std_logic_vector(to_unsigned(DEFAULT_CTRL, CONTROL_SIGNAL_WIDTH));

begin

    uut: entity work.generic_operation_decoder
    generic map (
        CONTROL_SIGNAL_WIDTH           => CONTROL_SIGNAL_WIDTH,
        OP_WIDTH                       => OP_WIDTH,
        OPERATION_CONTROL_SIGNAL_COUNT => OPERATION_CONTROL_SIGNAL_COUNT,
        OPERATION_TO_CONTROL_MAP       => OPERATION_TO_CONTROL_MAP,
        DEFAULT_CONTROL_SIGNAL         => DEFAULT_CONTROL_SIGNAL
    )
    port map (
        operation      => operation,
        control_signal => control_signal
    );

end architecture;