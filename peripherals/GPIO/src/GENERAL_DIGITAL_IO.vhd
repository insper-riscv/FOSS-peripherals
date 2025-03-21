library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;


entity GENERAL_DIGITAL_IO is
    port (
        --! Processors Clock
        clock         : in  std_logic;
        --! Synchronous Reset
        clear         : in  std_logic; 
        --! Data Input from Processor
        data_in       : in  std_logic;
        --! Control Signals
        write_dir     : in  std_logic:= '0'; 
        read_dir      : in  std_logic:= '0'; 
        write_out     : in  std_logic:= '0'; 
        toggle        : in  std_logic:= '0'; 
        read_out      : in  std_logic:= '0'; 
        read_external : in  std_logic:= '0';
        --! Data Output to Processor
        data_out      : out std_logic;
        --! Port Pin
        gpio_pin      : inout std_logic;
    );

end GENERAL_DIGITAL_IO;

architecture RTL of GENERAL_DIGITAL_IO is
    --! Data Read from the Pin after SYNC
    signal pin_input : std_logic;
    --! Pin Direction Stored in the Direction Flip-Flop
    signal pin_direction : std_logic;
    --! Pin Output Stored in the Output Flip-Flop
    signal pin_output : std_logic;
    --! Mux Selector: Selects wether to load data or to toggle the current value
    signal mux_sel : std_logic;
    --! Mux Output
    signal mux_out : std_logic;
    --! Enable Output Flip-Flop 
    signal enable_out : std_logic;
begin
    mux_sel <= toggle AND data_in;
    enable_out <= write_out OR mux_sel;
    --! Synchronizes the Data from the PIN
    PIN_SYNCHRONIZER : SYNCHRONIZER
        port map (
            clock  => clock,
            async_in => gpio_pin,
            sync_out  => pin_input
        );

    --! Tristate Buffer that only alters data out if pin is being read
    TRISTATE_PIN_INPUT : GENERIC_TRISTATE_BUFFER_1BIT
        port map (
            data_in       => pin_input,
            enable       => read_external,
            data_out      => data_out
        );

    --! Direction Flip Flop: Input "0", Output "1" 
    FF_DIR : GENERIC_FLIP_FLOP 
        port map (
            clock  => clock,
            clear  => clear,    
            enable => write_dir,    -- Enabled when writing direction
            source => data_in,
            state  => pin_direction
        );
    
    --! Tristate Buffer that only alters data out if direction is being read
    TRISTATE_DIRECTION_READ : GENERIC_TRISTATE_BUFFER_1BIT
        port map (
            data_in       => pin_direction,
            enable       => read_dir,
            data_out      => data_out
        );

      --! Mux writes data when sel = 0, toggles when sel = 1
    MUX_OUT : GENERIC_MUX_2X1 
        generic map (
            DATA_WIDTH => 1
        )
        port map (
            selector  => mux_sel,
            source_1  => data_in,    
            source_2 => NOT pin_output,  
            destination => mux_out
        );

    --! Output Flip Flop 
    FF_OUT : GENERIC_FLIP_FLOP 
        port map (
            clock  => clock,
            clear  => clear,    
            enable => enable_out,    -- Enabled when writing direction
            source => mux_out,
            state  => pin_output
        );

    --! Tristate Buffer that only alters pin if pin is output
    TRISTATE_OUTPUT_WRITE : GENERIC_TRISTATE_BUFFER_1BIT
        port map (
            data_in       => pin_output,
            enable       => pin_direction,
            data_out      => gpio_pin
        );

    --! Tristate Buffer that only alters data out if output is being read
    TRISTATE_OUTPUT_READ : GENERIC_TRISTATE_BUFFER_1BIT
        port map (
            data_in       => pin_output,
            enable       => read_out,
            data_out      => data_out
        );
end architecture;