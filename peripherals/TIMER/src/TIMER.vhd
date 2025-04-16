library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;

entity TIMER is
    generic (
        -- Data Bus Width
        DATA_WIDTH : integer := 32
    );
    port (
        -- Clock Signal
        clock       : in  std_logic;
        -- Clear Signal
        clear       : in  std_logic; 
        -- Data Inputed from the Processor
        data_in     : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        -- GPIO Address accessed by the Processor
        address     : in  STD_LOGIC_VECTOR(3 downto 0);
        -- Write Signal
        write       : in  std_logic; 
        -- Read Signal
        read        : in  std_logic; 
        -- Data Outputed to the Processor
        data_out    : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0)
    );
end entity;

architecture RTL of TIMER is

    -- Signals from the decoder
    signal dec_start_counter    : std_logic;
    signal dec_op_counter       : std_logic_vector(1 downto 0);
    signal dec_read_op     : std_logic;
    signal dec_load_reset_value : std_logic;

    -- Internal signals for counting
    signal enable_counter   : std_logic;
    signal current_count    : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal increment_value  : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal reset_value_reg  : std_logic_vector(DATA_WIDTH-1 downto 0);

    --! Mux output signals
    signal read_mux_out     : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal counter_mux_out    : std_logic_vector(DATA_WIDTH-1 downto 0);

begin
    -- Decoder instance: translates address, read, and write into control signals
    U_TIMER_OPERATION_DECODER : entity WORK.TIMER_OPERATION_DECODER
        port map (
            address          => address,
            read             => read,
            write            => write,
            start_counter    => dec_start_counter,
            op_counter       => dec_op_counter,
            load_reset_value => dec_load_reset_value,
            read_op     => dec_read_op
        );

    -- Flip-flop that latches '1' when start_counter is written, or resets on stop_counter
    U_START_STOP : entity WORK.GENERIC_FLIP_FLOP
        port map (
            clock  => clock,
            clear  => clear,
            enable => dec_start_counter,
            source => data_in,
            state  => enable_counter
        );
    
    -- Register to store the user-programmable reset value
    U_RESET_VALUE_REGISTER : entity WORK.GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable      => dec_load_reset_value,
            source      => data_in,
            destination => reset_value_reg
        );

    -- 4-to-1 multiplexer: selects the next value to load into the counter
    U_MUX_4X1 : entity WORK.GENERIC_MUX_4X1
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            selector     => dec_op_counter,   -- "00", "01", "10", or "11"
            source_1     => increment_value,  -- incremented count
            source_2     => data_in,          -- direct CPU load
            source_3     => reset_value_reg,  -- preset reset value
            source_4     => (others => '0'),  -- unused path
            destination  => counter_mux_out
        );
    
    -- Counter Register: updated with the multiplexer output while on Start Mode
    U_COUNTER_REGISTER : entity WORK.GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable      => enable_counter or write,
            source      => counter_mux_out,
            destination => current_count
        );

    -- Adder for increment operation (adds 1 to the current count)
    U_CONSTANT_ADDER : entity WORK.GENERIC_ADDER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            source_1    => current_count,
            source_2    => (others => '1'),
            destination => increment_value
        );
    
    -- Output Mux: selects the current count or placeholder value to output to the CPU
    U_OUTPUT_MUX : entity WORK.GENERIC_MUX_2X1
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            selector    => dec_read_op, -- "0" for current count, "1" for overflow
            source_1    => current_count, -- current count value
            source_2    => (others => '0'),  -- unused path
            destination => read_mux_out
        );
    -- Tristate Buffer: Transmits the Read Mux Output to data_out when read is '1'
    U_TRISTATE_BUFFER : entity WORK.GENERIC_TRISTATE_BUFFER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            data_in  => read_mux_out,
            enable   => (others => read),
            data_out => data_out
        );

end architecture;