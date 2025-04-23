library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity generic_uart is
    generic (
        -- Peripheral parameters
        DATA_WIDTH             : integer := 32;
        -- UART parameters
        UART_DATA_BITS         : integer := 8;
        COUNTER_WIDTH          : natural := 16
        -- Operation decoder parameters
        OP_WIDTH               : natural := 2;
        CONTROL_SIGNAL_WIDTH   : natural := 3;
        MAPPING_NUM            : natural := 3;
        OP_TO_CONTROL_MAP      : operation_mapping_matrix(0 to MAPPING_NUM-1, 0 to 1) := 
        ( 
            0 => (to_slv("00", OP_WIDTH-1 downto 0), to_slv("001", CONTROL_SIGNAL_WIDTH-1 downto 0)),
            1 => (to_slv("01", OP_WIDTH-1 downto 0), to_slv("010", CONTROL_SIGNAL_WIDTH-1 downto 0)),
            2 => (to_slv("10", OP_WIDTH-1 downto 0), to_slv("100", CONTROL_SIGNAL_WIDTH-1 downto 0))
        );
        DEFAULT_CONTROL_SIGNAL : std_logic_vector(CONTROL_SIGNAL_WIDTH-1 downto 0) := (others => '0')
    );
    port (
        -- Peripheral I/O
        clk         : in  std_logic;
        reset       : in  std_logic;
        data_i      : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        data_o      : out std_logic_vector(DATA_WIDTH-1 downto 0);
        wr_i        : in  std_logic; -- Write Enable
        rd_i        : in  std_logic; -- Read Enable
        operation   : in  std_logic_vector(OP_WIDTH-1 downto 0);

        -- UART I/O Pins
        rx_i        : in  std_logic;
        tx_o        : out std_logic;

        -- Periferal (UART) Interupt
        interrupt_o : out std_logic;
    );
end entity generic_uart;

architecture Structural of generic_uart is
    signal baud_tick : std_logic;

    -- Operation‐decoder outputs
    signal control_signal   : std_logic_vector(CONTROL_SIGNAL_WIDTH-1 downto 0);
    signal wr_config        : std_logic;
    signal wr_tx_op         : std_logic;
    signal rd_rx_op         : std_logic;
    
    -- Register outputs
    signal tx_reg_data      : std_logic_vector(UART_DATA_BITS-1 downto 0);
    signal rx_reg_data      : std_logic_vector(UART_DATA_BITS-1 downto 0);
    signal rx_reg_out       : std_logic_vector(UART_DATA_BITS-1 downto 0);

    signal config_reg_data  : std_logic_vector(DATA_WIDTH-1 downto 0);
    alias baud_div_i        : std_logic_vector(COUNTER_WIDTH-1 downto 0) is config_reg_data(COUNTER_WIDTH-1 downto 0);
    alias en_rx             : std_logic is config_reg_data(COUNTER_WIDTH);      -- next bit up
    alias en_tx             : std_logic is config_reg_data(COUNTER_WIDTH + 1);  -- next bit up

    signal wr_tx_strobe     : std_logic;
    signal wr_rx_reg_strobe : std_logic;
    signal rd_rx_strobe     : std_logic;
    
    wr_tx_strobe     <= wr_i and en_tx;
    rd_rx_strobe     <= rd_i and en_rx;
    wr_rx_reg_strobe <= rx_ready_o and en_rx;

begin

    operation_decoder: entity work.generic_operation_decoder
        generic map (
            OP_WIDTH               => OP_WIDTH,
            CONTROL_SIGNAL_WIDTH   => CONTROL_SIGNAL_WIDTH,
            MAPPING_NUM            => MAPPING_NUM,
            OP_TO_CONTROL_MAP      => OP_TO_CONTROL_MAP,
            DEFAULT_CONTROL_SIGNAL => DEFAULT_CONTROL_SIGNAL
        )
        port map (
            operation      => operation,
            control_signal => control_signal
        );
    
    -- steer wr_i/rd_i
    wr_config <= wr_i and control_signal(0);
    wr_tx_op  <= wr_i and control_signal(1);
    rd_rx_op  <= rd_i and control_signal(2);

    config_reg : entity work.generic_register
        generic map (
            WIDTH => DATA_WIDTH
        )
        port map (
            clk    => clk,
            reset  => reset,
            wr_i   => wr_config,
            data_i => data_i,
            data_o => config_reg_data
        );

    -- Baud generator
    baud_gen : entity work.generic_baud_generator
        generic map (
            COUNTER_WIDTH => COUNTER_WIDTH
        )
        port map (
            clk         => clk,
            reset       => reset,
            baud_div_i  => unsigned(baud_div_i),
            tick        => baud_tick
        );
    
    -- TX Register
    tx_reg : entity work.generic_register
        generic map (
            WIDTH => UART_DATA_BITS
        )
        port map (
            clk    => clk,
            reset  => reset,
            wr_i   => wr_tx_op,
            data_i => data_i(UART_DATA_BITS-1 downto 0),
            data_o => tx_reg_data
        );
    
    -- UART TX
    tx_uart : entity work.generic_uart_tx
        generic map (
            UART_DATA_BITS => UART_DATA_BITS
        )
        port map (
            clk            => clk,
            reset          => reset,
            tx_data_i      => tx_reg_data,
            write_strobe_i => wr_tx_strobe,
            baud_tick_i    => baud_tick,
            tx_o           => tx_o,
            tx_ready_o     => tx_ready_o
        );
    
    -- UART RX
    rx_uart : entity work.generic_uart_rx
        generic map (
            UART_DATA_BITS => UART_DATA_BITS
        )
        port map (
            clk            => clk,
            reset          => reset,
            rx_i           => rx_i,
            baud_tick_i    => baud_tick,
            rx_data_o      => rx_reg_data,
            rx_ready_o     => rx_ready_o,
            read_strobe_i  => rd_rx_strobe,
            parity_error_o => parity_error_o
        );
    
    -- RX Register
    rx_reg : entity work.generic_register
        generic map (
            WIDTH => UART_DATA_BITS
        )
        port map (
            clk    => clk,
            reset  => reset,
            wr_i   => wr_rx_reg_strobe,
            data_i => rx_reg_data,
            data_o => rx_reg_out
        );

    -- Interrupt
    interrupt_o <= '1' when ((rx_ready_o and en_rx) or (tx_ready_o and en_tx) or parity_error_o) else '0';

    -- Multiplex data_o back to bus
    data_o <= config_reg_data                                            when control_signal = "001" else -- config read
              (DATA_WIDTH-UART_DATA_BITS-1 downto 0 => '0') & rx_reg_out when control_signal = "100" else -- rx read
              (others => '0');

end architecture Structural;