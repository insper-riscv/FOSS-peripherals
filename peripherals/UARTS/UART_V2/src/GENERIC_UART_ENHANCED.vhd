library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.types.all;

entity generic_uart_enhanced is
    generic (
        -- Peripheral parameters
        DATA_WIDTH             : integer := 32;

        -- UART parameters
        UART_DATA_BITS         : integer := 8;
        COUNTER_WIDTH          : natural := 16;
        FRACTIONAL_WIDTH       : natural := 8;
        
        -- FIFO parameters
        TX_FIFO_DEPTH          : natural := 16;
        RX_FIFO_DEPTH          : natural := 16;

        -- Operation decoder parameters
        OP_WIDTH               : natural := 3;  -- Expanded for more operations
        CONTROL_SIGNAL_WIDTH   : natural := 4;  -- Expanded for more control signals
        OPERATION_CONTROL_SIGNAL_COUNT : natural := 6;
        OPERATION_TO_CONTROL_MAP : op_cs_map(0 to OPERATION_CONTROL_SIGNAL_COUNT-1) := (
            0 => (op   => std_logic_vector(to_unsigned(0, OP_WIDTH)),  -- Config write/read
                  ctrl => std_logic_vector(to_unsigned(1, CONTROL_SIGNAL_WIDTH))),
            1 => (op   => std_logic_vector(to_unsigned(1, OP_WIDTH)),  -- TX data write
                  ctrl => std_logic_vector(to_unsigned(2, CONTROL_SIGNAL_WIDTH))),
            2 => (op   => std_logic_vector(to_unsigned(2, OP_WIDTH)),  -- RX data read
                  ctrl => std_logic_vector(to_unsigned(4, CONTROL_SIGNAL_WIDTH))),
            3 => (op   => std_logic_vector(to_unsigned(3, OP_WIDTH)),  -- Status read
                  ctrl => std_logic_vector(to_unsigned(8, CONTROL_SIGNAL_WIDTH))),
            4 => (op   => std_logic_vector(to_unsigned(4, OP_WIDTH)),  -- Baud config
                  ctrl => std_logic_vector(to_unsigned(1, CONTROL_SIGNAL_WIDTH))),
            5 => (op   => std_logic_vector(to_unsigned(5, OP_WIDTH)),  -- FIFO control
                  ctrl => std_logic_vector(to_unsigned(1, CONTROL_SIGNAL_WIDTH)))
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

        -- Enhanced Interrupts
        tx_interrupt_o    : out std_logic;  -- TX FIFO threshold
        rx_interrupt_o    : out std_logic;  -- RX FIFO threshold  
        error_interrupt_o : out std_logic   -- Error conditions
    );
end entity generic_uart_enhanced;

architecture Structural of generic_uart_enhanced is
    signal baud_tick : std_logic;

    -- Operation decoder outputs
    signal control_signal   : std_logic_vector(CONTROL_SIGNAL_WIDTH-1 downto 0);
    signal wr_config        : std_logic;
    signal wr_tx_op         : std_logic;
    signal rd_rx_op         : std_logic;
    signal rd_status_op     : std_logic;
    
    -- Configuration registers
    signal config_reg_data  : std_logic_vector(DATA_WIDTH-1 downto 0);
    alias baud_div_i        : std_logic_vector(COUNTER_WIDTH-1 downto 0) is config_reg_data(COUNTER_WIDTH-1 downto 0);
    alias baud_frac_i       : std_logic_vector(FRACTIONAL_WIDTH-1 downto 0) is config_reg_data(COUNTER_WIDTH+FRACTIONAL_WIDTH-1 downto COUNTER_WIDTH);
    alias fractional_en     : std_logic is config_reg_data(COUNTER_WIDTH + FRACTIONAL_WIDTH);
    alias en_rx             : std_logic is config_reg_data(COUNTER_WIDTH + FRACTIONAL_WIDTH + 1);
    alias en_tx             : std_logic is config_reg_data(COUNTER_WIDTH + FRACTIONAL_WIDTH + 2);

    -- TX FIFO signals
    signal tx_wr_strobe     : std_logic;
    signal tx_empty         : std_logic;
    signal tx_full          : std_logic;
    signal tx_almost_full   : std_logic;
    signal tx_busy          : std_logic;
    signal tx_threshold     : std_logic;

    -- RX FIFO signals
    signal rx_rd_strobe     : std_logic;
    signal rx_data_out      : std_logic_vector(UART_DATA_BITS-1 downto 0);
    signal rx_empty         : std_logic;
    signal rx_full          : std_logic;
    signal rx_almost_full   : std_logic;
    signal rx_data_ready    : std_logic;
    signal rx_threshold     : std_logic;

    -- Error signals
    signal parity_error     : std_logic;
    signal frame_error      : std_logic;
    signal overrun_error    : std_logic;

    -- Status register construction
    signal status_reg       : std_logic_vector(DATA_WIDTH-1 downto 0);

begin
    -- Control signal decoding
    wr_config    <= wr_i and control_signal(0);
    wr_tx_op     <= wr_i and control_signal(1) and en_tx;
    rd_rx_op     <= rd_i and control_signal(2);
    rd_status_op <= rd_i and control_signal(3);

    -- TX/RX strobes
    tx_wr_strobe <= wr_tx_op and not tx_full;  -- Prevent writes to full FIFO
    rx_rd_strobe <= rd_rx_op and not rx_empty; -- Prevent reads from empty FIFO

    -- Interrupt generation
    tx_interrupt_o <= tx_threshold and en_tx;
    rx_interrupt_o <= rx_threshold and en_rx;
    error_interrupt_o <= parity_error or frame_error or overrun_error;

    -- Status register construction
    status_reg <= (
        0 => tx_empty,
        1 => tx_full,
        2 => tx_almost_full,
        3 => tx_busy,
        4 => rx_empty,
        5 => rx_full,
        6 => rx_almost_full,
        7 => rx_data_ready,
        8 => parity_error,
        9 => frame_error,
        10 => overrun_error,
        11 => tx_threshold,
        12 => rx_threshold,
        others => '0'
    );

    operation_decoder: entity work.generic_operation_decoder
        generic map (
            OP_WIDTH                       => OP_WIDTH,
            CONTROL_SIGNAL_WIDTH           => CONTROL_SIGNAL_WIDTH,
            OPERATION_CONTROL_SIGNAL_COUNT => OPERATION_CONTROL_SIGNAL_COUNT,
            OPERATION_TO_CONTROL_MAP       => OPERATION_TO_CONTROL_MAP,
            DEFAULT_CONTROL_SIGNAL         => DEFAULT_CONTROL_SIGNAL
        )
        port map (
            operation      => operation,
            control_signal => control_signal
        );

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

    -- Enhanced Baud generator
    baud_gen : entity work.generic_baud_generator_enhanced
        generic map (
            COUNTER_WIDTH    => COUNTER_WIDTH,
            FRACTIONAL_WIDTH => FRACTIONAL_WIDTH
        )
        port map (
            clk             => clk,
            reset           => reset,
            baud_div_i      => unsigned(baud_div_i),
            baud_frac_i     => unsigned(baud_frac_i),
            fractional_en_i => fractional_en,
            tick            => baud_tick,
            counter_debug_o => open
        );

    -- Enhanced UART TX with FIFO
    tx_uart_fifo : entity work.generic_uart_tx_fifo
        generic map (
            DATA_BITS  => UART_DATA_BITS,
            FIFO_DEPTH => TX_FIFO_DEPTH
        )
        port map (
            clk              => clk,
            reset            => reset,
            tx_data_i        => data_i(UART_DATA_BITS-1 downto 0),
            write_strobe_i   => tx_wr_strobe,
            baud_tick_i      => baud_tick,
            tx_o             => tx_o,
            tx_busy_o        => tx_busy,
            tx_empty_o       => tx_empty,
            tx_full_o        => tx_full,
            tx_almost_full_o => tx_almost_full,
            tx_threshold_o   => tx_threshold
        );

    -- Enhanced UART RX with FIFO
    rx_uart_fifo : entity work.generic_uart_rx_fifo
        generic map (
            DATA_BITS  => UART_DATA_BITS,
            FIFO_DEPTH => RX_FIFO_DEPTH
        )
        port map (
            clk              => clk,
            reset            => reset,
            rx_i             => rx_i,
            baud_tick_i      => baud_tick,
            rx_data_o        => rx_data_out,
            read_strobe_i    => rx_rd_strobe,
            rx_empty_o       => rx_empty,
            rx_full_o        => rx_full,
            rx_almost_full_o => rx_almost_full,
            rx_data_ready_o  => rx_data_ready,
            parity_error_o   => parity_error,
            frame_error_o    => frame_error,
            overrun_error_o  => overrun_error,
            rx_threshold_o   => rx_threshold
        );

    -- Output data multiplexing
    data_o <= config_reg_data when control_signal = "0001" else -- config read
              status_reg when control_signal = "1000" else      -- status read
              (DATA_WIDTH-UART_DATA_BITS-1 downto 0 => '0') & rx_data_out when control_signal = "0100" else -- rx read
              (others => '0');

end architecture Structural; 