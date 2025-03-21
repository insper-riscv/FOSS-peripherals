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
    --! Decoded Operation Signals
    signal op_vec : std_logic_vector(7 downto 0);
begin
    --! Decodes the Operation based on the Address and the Read/Write Signals
    DECODER: GPIO_OPERATION_DECODER
        port map (
            address => address,
            write   => write,
            read    => read,
            data_out => op_vec
        );
    --! For each GPIO Pin, instantiate a General Digital IO
    GENERAL_DIGITALS: for i in 0 to DATA_WIDTH-1 generate
        GENERAL_DIGITAL: entity work.GENERAL_DIGITAL_IO
            port map (
                clock         => clock,
                clear         => clear,
                data_in       => data_in(i),
                write_dir     => op_vec(0),
                read_dir      => op_vec(1),
                write_out     => op_vec(2),
                toggle        => op_vec(3),
                read_out      => op_vec(4),
                read_external => op_vec(5),
                data_out      => data_out(i),
                gpio_pin      => gpio_pins(i)
            );
    end generate;
   
end architecture;
