library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity generic_uart is
    generic (
        DATA_BITS : integer := 8;
        COUNTER_WIDTH : natural := 16
    );
    port (
        clk            : in  std_logic;
        reset          : in  std_logic;

        -- Serial I/O
        rx_i           : in  std_logic;
        tx_o           : out std_logic;

        -- Baud rate
        baud_div_i     : in  unsigned(COUNTER_WIDTH-1 downto 0);

        -- UART TX
        wr_tx_i        : in  std_logic;
        tx_data_i      : in  std_logic_vector(DATA_BITS-1 downto 0);
        tx_ready_o     : out std_logic;

        -- UART RX
        rd_rx_i        : in  std_logic;
        rx_data_o      : out std_logic_vector(DATA_BITS-1 downto 0);
        rx_ready_o     : out std_logic;
        parity_error_o : out std_logic;
    );
end entity generic_uart;

architecture Structural of generic_uart is
    signal baud_tick : std_logic;
    
    -- Register outputs
    signal tx_reg_data : std_logic_vector(DATA_BITS-1 downto 0);
    signal rx_reg_data : std_logic_vector(DATA_BITS-1 downto 0);

begin
    -- Baud generator
    baud_gen : entity work.generic_baud_generator
        generic map (
            COUNTER_WIDTH => COUNTER_WIDTH
        )
        port map (
            clk         => clk,
            reset       => reset,
            baud_div_i  => baud_div_i,
            tick        => baud_tick
        );
    
    -- TX Register
    tx_reg : entity work.generic_register
        generic map (
            WIDTH => DATA_BITS
        )
        port map (
            clk    => clk,
            reset  => reset,
            wr_i   => wr_tx_i,
            data_i => tx_data_i,
            data_o => tx_reg_data
        );
    
    -- UART TX
    tx_uart : entity work.generic_uart_tx
        generic map (
            DATA_BITS => DATA_BITS
        )
        port map (
            clk            => clk,
            reset          => reset,
            tx_data_i      => tx_reg_data,
            write_strobe_i => wr_tx_i,
            baud_tick_i    => baud_tick,
            tx_o           => tx_o,
            tx_ready_o     => tx_ready_o
        );
    
    -- UART RX
    rx_uart : entity work.generic_uart_rx
        generic map (
            DATA_BITS => DATA_BITS
        )
        port map (
            clk            => clk,
            reset          => reset,
            rx_i           => rx_i,
            baud_tick_i    => baud_tick,
            rx_data_o      => rx_reg_data,
            rx_ready_o     => rx_ready_o,
            read_strobe_i  => rd_rx_i,
            parity_error_o => parity_error_o
        );
    
    -- RX Register
    rx_reg : entity work.generic_register
        generic map (
            WIDTH => DATA_BITS
        )
        port map (
            clk    => clk,
            reset  => reset,
            wr_i   => rx_ready_o,
            data_i => rx_reg_data,
            data_o => rx_data_o
        );
end architecture Structural;