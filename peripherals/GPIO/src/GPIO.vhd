library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;

entity GPIO is
    generic (
        --! Data Width
        DATA_WIDTH : integer := 32
    );
    port (
        --! Clock Signal
        clock       : in  std_logic;
        --! Clear Signal
        clear       : in  std_logic; 
        --! Data Inputed from the Processor
        data_in     : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! GPIO Address accessed by the Processor
        address     : in  STD_LOGIC_VECTOR(2 downto 0);
        --! Write Signal
        write       : in  std_logic; 
        --! Read Signal
        read        : in  std_logic; 
        --! Data Outputed to the Processor
        data_out    : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! GPIO Pins
        gpio_pins   : inout std_logic_vector(DATA_WIDTH-1 downto 0)
    );
end GPIO;

architecture RTL of GPIO is

    --! GPIO Operation Decoder
    signal dir_enable : std_logic;
    signal write_op   : std_logic_vector(1 downto 0);
    signal read_op    : std_logic_vector(1 downto 0);

    --! Internal Registers
    signal reg_out    : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal reg_dir    : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal reg_input  : std_logic_vector(DATA_WIDTH-1 downto 0);

    --! Mux output signals
    signal mux_write  : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal mux_read   : std_logic_vector(DATA_WIDTH-1 downto 0);

begin

    --! Decode the GPIO Address
    U_OP_DEC : entity WORK.GPIO_OPERATION_DECODER
        port map (
            address    => address,
            dir_enable => dir_enable,
            write_op   => write_op,
            read_op    => read_op
        );

    --! Direction Register
    U_REG_DIR : entity WORK.GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable      => dir_enable AND write,
            source      => data_in,
            destination => reg_dir
        );

    --! Mux Write Operations: Load, Set, Clear, Toggle
    U_MUX_WRITE : entity WORK.GENERIC_MUX_4X1
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            selector    => write_op,
            source_1    => data_in,
            source_2    => reg_out OR data_in,
            source_3    => reg_out AND (NOT data_in),
            source_4    => reg_out XOR data_in,
            destination => mux_write
        );

    --! Output Register
    U_REG_OUT : entity WORK.GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable      => write AND NOT dir_enable,
            source      => mux_write,
            destination => reg_out
        );

    --! Tristate Buffer for GPIO Pins
    U_GPIO_BUFFER : entity WORK.GENERIC_TRISTATE_BUFFER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            data_in  => reg_out,
            enable   => reg_dir,
            data_out => gpio_pins
        );

    --! Synchronizer for GPIO Pins
    U_SYNC : entity WORK.GENERIC_SYNCHRONIZER
        generic map (
            DATA_WIDTH => DATA_WIDTH,
            N          => 2
        )
        port map (
            clock       => clock,
            async_in  => gpio_pins,
            sync_out  => reg_input
        );

    --! Mux Read Operations: Read Dir, Read Out, Read Ext
    U_MUX_READ : entity WORK.GENERIC_MUX_4X1
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            selector    => read_op,
            source_1    => reg_dir,
            source_2    => reg_out,
            source_3    => reg_input,
            source_4    => (others => '0'),
            destination => mux_read
        );

    --! Read Tristate Buffer
    U_GPIO_READ : entity WORK.GENERIC_TRISTATE_BUFFER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            data_in  => mux_read,
            enable   => (others => read),
            data_out => data_out
        );

end architecture;
